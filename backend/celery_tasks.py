# backend/celery_tasks.py
from celery import Celery
from scraper.amazon_scraper import scrape_amazon_reviews
from nlp.fake_detector import predict_fake_ensemble
from app.database import SessionLocal
from app.models import ProductLink
from datetime import datetime
import logging

# Celery config
celery = Celery("reputrack", broker="redis://default:AXr_AAIncDJjNGE2ZTc5M2JiYmM0YjQ0OWE2OTlmZjdlYjU5YzJmNXAyMzE0ODc@factual-dodo-31487.upstash.io:6379")

@celery.task
def scrape_and_analyze_all():
    db = SessionLocal()
    links = db.query(ProductLink).filter(ProductLink.platform == "amazon").all()

    for link in links:
        try:
            print(f"Scraping: {link.url}")
            result = scrape_amazon_reviews(link.url, headless=True)

            if result.get("reviews"):
                analyzed_reviews, fake_ratio = predict_fake_ensemble(result["reviews"])
                old_rating = link.last_rating or 0
                new_rating = result["rating"] or 0

                link.last_rating = new_rating
                link.fake_ratio = fake_ratio
                link.reviews_json = analyzed_reviews
                link.last_scraped = datetime.utcnow()
                link.scrape_note = f"Success: {len(analyzed_reviews)} reviews"

                # Rating drop detection
                if new_rating > 0 and old_rating > new_rating + 0.5:
                    link.scrape_note += f" | RATING DROPPED from {old_rating} to {new_rating}"

            else:
                link.scrape_note = result.get("note", "No reviews")

            db.commit()
            print(f"Done: {link.product.name}")

        except Exception as e:
            link.scrape_note = f"Error: {str(e)}"
            db.commit()
            print(f"Failed: {e}")

    db.close()