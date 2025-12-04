# backend/scraper/additional_scrapers.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import random
import re

def scrape_myntra_reviews(url: str, headless=True):
    """Myntra - Fashion platform with clean structure"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = context.new_page()

        try:
            print(f"[MYNTRA] Navigating to: {url}")
            page.goto(url, timeout=60000, wait_until='domcontentloaded')
            time.sleep(random.uniform(2, 4))
            
            # Extract rating
            rating = None
            rating_selectors = [
                'div.index-overallRating',
                'div[class*="rating"]',
                'span.index-overallRating',
            ]
            
            for sel in rating_selectors:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0:
                        text = el.inner_text(timeout=5000).strip()
                        match = re.search(r'(\d+\.?\d*)', text)
                        if match:
                            rating = float(match.group(1))
                            print(f"[MYNTRA] Rating found: {rating}")
                            break
                except:
                    continue
            
            # Scroll to reviews
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.7)")
            time.sleep(2)
            
            # Extract reviews
            reviews = []
            review_selectors = [
                'div.detailed-reviews-userReviewsContainer',
                'div[class*="userReview"]',
                'div.user-review-main',
            ]
            
            print("[MYNTRA] Looking for reviews...")
            for sel in review_selectors:
                try:
                    page.wait_for_selector(sel, timeout=10000)
                    review_elements = page.locator(sel).all()
                    
                    if len(review_elements) > 0:
                        print(f"[MYNTRA] Found {len(review_elements)} reviews with: {sel}")
                        
                        for idx, el in enumerate(review_elements[:10]):
                            try:
                                text = el.inner_text(timeout=3000).strip()
                                
                                # Extract star rating
                                stars = 5
                                star_match = re.search(r'(\d+)★', text)
                                if star_match:
                                    stars = int(star_match.group(1))
                                
                                # Clean text
                                lines = [line.strip() for line in text.split('\n') if line.strip()]
                                # Usually review text is the longest line
                                text = max(lines, key=len) if lines else text
                                text = re.sub(r'\d+★', '', text)
                                text = text.strip()
                                
                                if len(text) > 20:
                                    reviews.append({"text": text, "stars": stars})
                                    print(f"[MYNTRA] Extracted review {idx + 1}: {stars} stars")
                            except:
                                continue
                        break
                except PlaywrightTimeout:
                    continue
            
            browser.close()
            print(f"[MYNTRA] Final: {len(reviews)} reviews, rating: {rating}")
            return {"rating": rating, "reviews": reviews}

        except Exception as e:
            print(f"[MYNTRA] Error: {e}")
            browser.close()
            return {"error": str(e), "rating": None, "reviews": []}



def scrape_snapdeal_reviews(url: str, headless=True):
    """Snapdeal - Older platform, stable selectors"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = context.new_page()

        try:
            print(f"[SNAPDEAL] Navigating to: {url}")
            page.goto(url, timeout=60000, wait_until='domcontentloaded')
            time.sleep(random.uniform(2, 4))
            
            # Extract rating
            rating = None
            rating_selectors = [
                'span.avrg-rating',
                'div[class*="rating"]',
                'span.filled-stars',
            ]
            
            for sel in rating_selectors:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0:
                        text = el.inner_text(timeout=5000).strip()
                        match = re.search(r'(\d+\.?\d*)', text)
                        if match:
                            rating = float(match.group(1))
                            print(f"[SNAPDEAL] Rating found: {rating}")
                            break
                except:
                    continue
            
            # Scroll to reviews
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
            time.sleep(2)
            
            # Extract reviews
            reviews = []
            review_selectors = [
                'div.user-review',
                'div[class*="review-box"]',
                'li.review-list',
            ]
            
            print("[SNAPDEAL] Looking for reviews...")
            for sel in review_selectors:
                try:
                    page.wait_for_selector(sel, timeout=10000)
                    review_elements = page.locator(sel).all()
                    
                    if len(review_elements) > 0:
                        print(f"[SNAPDEAL] Found {len(review_elements)} reviews with: {sel}")
                        
                        for idx, el in enumerate(review_elements[:10]):
                            try:
                                text = el.inner_text(timeout=3000).strip()
                                
                                # Extract star rating
                                stars = 5
                                star_match = re.search(r'(\d+)★', text)
                                if star_match:
                                    stars = int(star_match.group(1))
                                
                                # Clean text
                                lines = [line.strip() for line in text.split('\n') if line.strip()]
                                text = max(lines, key=len) if lines else text
                                text = re.sub(r'\d+★', '', text)
                                text = text.strip()
                                
                                if len(text) > 20:
                                    reviews.append({"text": text, "stars": stars})
                                    print(f"[SNAPDEAL] Extracted review {idx + 1}: {stars} stars")
                            except:
                                continue
                        break
                except PlaywrightTimeout:
                    continue
            
            browser.close()
            print(f"[SNAPDEAL] Final: {len(reviews)} reviews, rating: {rating}")
            return {"rating": rating, "reviews": reviews}

        except Exception as e:
            print(f"[SNAPDEAL] Error: {e}")
            browser.close()
            return {"error": str(e), "rating": None, "reviews": []}