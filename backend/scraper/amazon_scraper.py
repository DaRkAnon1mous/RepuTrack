# backend/scraper/amazon_scraper.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import random

def scrape_amazon_reviews(url: str, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Anti-detection
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = context.new_page()

        try:
            print(f"Navigating to: {url}")
            
            # FIX 1: Remove networkidle - use domcontentloaded only
            page.goto(url, timeout=60000, wait_until='domcontentloaded')
            time.sleep(random.uniform(2, 4))  # Let page settle
            
            print("Page loaded, extracting data...")
            
            # FIX 2: Extract rating first (it's always visible)
            rating = None
            rating_selectors = [
                'span[data-hook="rating-out-of-text"]',
                'i[data-hook="average-star-rating"] span.a-icon-alt',
                'span.a-icon-alt'
            ]
            
            for sel in rating_selectors:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0:
                        text = el.inner_text(timeout=5000)
                        print(f"Found rating text: {text}")
                        # Extract number (e.g., "4.2 out of 5 stars" -> 4.2)
                        if 'out of' in text.lower():
                            rating = float(text.split()[0])
                        elif 'stars' in text.lower():
                            rating = float(text.split()[0])
                        break
                except Exception as e:
                    print(f"Selector {sel} failed: {e}")
                    continue
            
            print(f"Rating found: {rating}")
            
            # FIX 3: Scroll to reviews section first
            try:
                reviews_section = page.locator('div[data-hook="reviews-medley-footer"], div#reviewsMedley').first
                if reviews_section.count() > 0:
                    reviews_section.scroll_into_view_if_needed(timeout=5000)
                    time.sleep(2)
            except:
                # Scroll manually if section not found
                page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.5)")
                time.sleep(2)
            
            print("Looking for reviews...")
            
            # FIX 4: Check if we need to click "See all reviews"
            reviews = []
            try:
                # Try to find reviews on current page first
                page.wait_for_selector('[data-hook="review"]', timeout=10000)
                print("Reviews found on main page")
                
            except PlaywrightTimeout:
                # If not found, click "See all reviews"
                print("No reviews on main page, trying 'See more reviews' link")
                try:
                    see_all_link = page.locator('a[data-hook="see-all-reviews-link-foot"]').first
                    if see_all_link.count() > 0:
                        see_all_link.click()
                        page.wait_for_load_state('domcontentloaded')
                        time.sleep(2)
                        print("Navigated to reviews page")
                except Exception as e:
                    print(f"Could not navigate to reviews page: {e}")
            
            # FIX 5: Extract reviews with better error handling
            try:
                page.wait_for_selector('[data-hook="review"]', timeout=15000)
                review_elements = page.locator('[data-hook="review"]').all()
                print(f"Found {len(review_elements)} review elements")
                
                for idx, el in enumerate(review_elements):  # Get first 10
                    try:
                        # Get review text
                        text_el = el.locator('[data-hook="review-body"] span').first
                        if text_el.count() == 0:
                            text_el = el.locator('[data-hook="review-body"]').first
                        
                        text = text_el.inner_text(timeout=3000).strip()
                        
                        # Get star rating
                        star_el = el.locator('[data-hook="review-star-rating"] span.a-icon-alt, [data-hook="cmps-review-star-rating"] span.a-icon-alt').first
                        stars = 5  # Default
                        
                        if star_el.count() > 0:
                            star_text = star_el.inner_text(timeout=3000)
                            try:
                                stars = int(float(star_text.split()[0]))
                            except:
                                stars = 5
                        
                        if len(text) > 0:  # Valid review
                            reviews.append({"text": text, "stars": stars})
                            print(f"Extracted review {idx + 1}: {stars} stars, {len(text)} chars")
                    
                    except Exception as e:
                        print(f"Error extracting review {idx + 1}: {e}")
                        continue
            
            except PlaywrightTimeout:
                print("No reviews found after waiting")
            
            browser.close()
            
            result = {"rating": rating, "reviews": reviews}
            print(f"\nFinal result: {len(reviews)} reviews, rating: {rating}")
            return result

        except Exception as e:
            print(f"Error occurred: {e}")
            browser.close()
            return {"error": str(e), "rating": None, "reviews": []}