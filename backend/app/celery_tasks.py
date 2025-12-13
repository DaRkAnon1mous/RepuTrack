# backend/celery_tasks.py
from celery import Celery
from ..scraper.amazon_scraper import scrape_amazon_reviews
from ..nlp.fake_detector import predict_fake_ensemble
from .database import SessionLocal
from .models import ProductLink, Product
from ..nlp.sentiment_analyzer import analyze_sentiment
from datetime import datetime
import logging
import os 
from dotenv import load_dotenv
load_dotenv()
# Celery config
celery = Celery("reputrack", broker=os.getenv("REDIS_URL"))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Resend
resend= os.getenv("RESEND_API_KEY")


def send_rating_drop_email(user_email, product_name, old_rating, new_rating, product_url):
    """Send email notification when rating drops"""
    try:
        email_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                    <h1 style="color: white; margin: 0;">⚠️ Rating Alert</h1>
                </div>
                
                <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #1f2937;">Rating Drop Detected!</h2>
                    <p style="color: #4b5563; font-size: 16px;">
                        The product you're tracking has experienced a significant rating drop:
                    </p>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ef4444;">
                        <h3 style="color: #1f2937; margin-top: 0;">{product_name}</h3>
                        <div style="display: flex; justify-content: space-around; margin: 15px 0;">
                            <div>
                                <p style="color: #6b7280; margin: 0; font-size: 14px;">Previous Rating</p>
                                <p style="color: #1f2937; margin: 5px 0; font-size: 24px; font-weight: bold;">⭐ {old_rating:.1f}</p>
                            </div>
                            <div style="color: #ef4444; font-size: 30px; align-self: center;">→</div>
                            <div>
                                <p style="color: #6b7280; margin: 0; font-size: 14px;">Current Rating</p>
                                <p style="color: #ef4444; margin: 5px 0; font-size: 24px; font-weight: bold;">⭐ {new_rating:.1f}</p>
                            </div>
                        </div>
                    </div>
                    
                    <p style="color: #4b5563;">
                        This could indicate issues with product quality or an increase in negative reviews. 
                        We recommend checking the recent reviews on Amazon.
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{product_url}" 
                           style="background: #1f2937; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">
                            View on Amazon
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    
                    <p style="color: #9ca3af; font-size: 12px; text-align: center;">
                        You're receiving this because you're tracking this product on RepuTrack.<br>
                        This is an automated notification from your product monitoring system.
                    </p>
                </div>
            </body>
        </html>
        """
        
        params = {
            "from": "RepuTrack <onboarding@resend.dev>",  # Change this to your verified domain
            "to": [user_email],
            "subject": f"⚠️ Rating Drop Alert: {product_name}",
            "html": email_html,
        }
        
        email = resend.Emails.send(params)
        logger.info(f"✓ Email sent to {user_email}: {email}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to send email: {e}")
        return False


@celery.task
def scrape_single_product(product_id: int):
    """Scrape a single product immediately after creation"""
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            logger.error(f"Product {product_id} not found")
            return {"error": "Product not found"}

        logger.info(f"Starting scrape for product: {product.name}")
        
        for link in product.links:
            if link.platform != "amazon":
                continue
                
            try:
                logger.info(f"Scraping: {link.url}")
                result = scrape_amazon_reviews(link.url, headless=True)

                if result.get("reviews"):
                    # 1. Fake review detection
                    analyzed_reviews, fake_ratio = predict_fake_ensemble(result["reviews"])
                    
                    # 2. Sentiment analysis
                    analyzed_reviews, sentiment_score, sentiment_breakdown = analyze_sentiment(analyzed_reviews)
                    
                    link.last_rating = result.get("rating", 0)
                    link.fake_ratio = fake_ratio
                    link.sentiment_score = sentiment_score
                    link.reviews_json = analyzed_reviews
                    link.last_scraped = datetime.utcnow()
                    link.scrape_note = f"Success: {len(analyzed_reviews)} reviews analyzed"
                    
                    logger.info(f"✓ Analyzed {len(analyzed_reviews)} reviews")
                    logger.info(f"  - Fake ratio: {fake_ratio:.2%}")
                    logger.info(f"  - Sentiment: {sentiment_score:.2f} (Pos: {sentiment_breakdown['positive']}, Neg: {sentiment_breakdown['negative']}, Neu: {sentiment_breakdown['neutral']})")
                else:
                    link.scrape_note = result.get("note", "No reviews found")
                    logger.warning(f"No reviews found for {link.url}")

            except Exception as e:
                link.scrape_note = f"Error: {str(e)}"
                logger.error(f"Error scraping {link.url}: {e}")

        db.commit()
        logger.info(f"✓ Completed scraping for: {product.name}")
        return {"status": "completed", "product_id": product_id}

    except Exception as e:
        logger.error(f"Fatal error for product {product_id}: {e}")
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


@celery.task
def scrape_and_analyze_all():
    """Scheduled task to scrape all products"""
    db = SessionLocal()
    links = db.query(ProductLink).filter(ProductLink.platform == "amazon").all()

    logger.info(f"Starting scheduled scrape for {len(links)} links")

    for link in links:
        try:
            logger.info(f"Scraping: {link.url}")
            result = scrape_amazon_reviews(link.url, headless=True)

            if result.get("reviews"):
                # Fake detection
                analyzed_reviews, fake_ratio = predict_fake_ensemble(result["reviews"])
                
                # Sentiment analysis
                analyzed_reviews, sentiment_score, sentiment_breakdown = analyze_sentiment(analyzed_reviews)
                
                old_rating = link.last_rating or 0
                new_rating = result["rating"] or 0

                link.last_rating = new_rating
                link.fake_ratio = fake_ratio
                link.sentiment_score = sentiment_score
                link.reviews_json = analyzed_reviews
                link.last_scraped = datetime.utcnow()
                link.scrape_note = f"Success: {len(analyzed_reviews)} reviews"

                # Rating drop detection - Send email
                if new_rating > 0 and old_rating > 0 and old_rating > new_rating + 0.5:
                    link.scrape_note += f" | RATING DROPPED from {old_rating} to {new_rating}"
                    logger.warning(f"⚠️  Rating drop detected: {old_rating} → {new_rating}")
                    
                    # Send email notification
                    user_email = link.product.user.email
                    send_rating_drop_email(
                        user_email=user_email,
                        product_name=link.product.name,
                        old_rating=old_rating,
                        new_rating=new_rating,
                        product_url=link.url
                    )

            else:
                link.scrape_note = result.get("note", "No reviews")

            db.commit()
            logger.info(f"✓ Done: {link.product.name}")

        except Exception as e:
            link.scrape_note = f"Error: {str(e)}"
            db.commit()
            logger.error(f"✗ Failed: {e}")

    db.close()
    logger.info("✓ Scheduled scrape completed")