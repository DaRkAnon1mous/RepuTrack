# backend/scraper/myntra_scraper.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import random

def scrape_myntra_reviews(url: str, headless=True):
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
            print(f"Navigating to Myntra: {url}")
            
            page.goto(url, timeout=60000, wait_until='domcontentloaded')
            time.sleep(random.uniform(2, 4))
            
            print("Page loaded, extracting data...")
            
            # Extract overall rating
            rating = None
            rating_selectors = [
                'div.rating',
                'div.rating-average',
                'div.index-overallRating',
                'span.rating-count',
                'div[class*="rating"]',
                'div[class*="Rating"]'
            ]
            
            for sel in rating_selectors:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0:
                        text = el.inner_text(timeout=5000)
                        print(f"Found rating text: {text}")
                        # Extract numeric rating
                        import re
                        numbers = re.findall(r'(\d+\.?\d*)', text)
                        if numbers:
                            rating = float(numbers[0])
                            if rating > 5:  # If it's out of 10, convert to 5
                                rating = rating / 2
                            break
                except Exception as e:
                    print(f"Selector {sel} failed: {e}")
                    continue
            
            print(f"Rating found: {rating}")
            
            # Scroll to reviews section
            try:
                # Myntra reviews are usually in a specific section
                reviews_section = page.locator('div.user-reviews, div.ratings-reviews, div.reviews-container, div.index-reviews').first
                if reviews_section.count() > 0:
                    reviews_section.scroll_into_view_if_needed(timeout=5000)
                    time.sleep(2)
            except:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
                time.sleep(2)
            
            print("Looking for reviews...")
            
            # Check for "Show More" or "View All Reviews" button
            reviews = []
            try:
                # Try to find reviews on current page
                page.wait_for_selector('div.user-review, div.review, div.userReview, div[class*="review"]', timeout=10000)
                print("Reviews found on main page")
                
            except PlaywrightTimeout:
                # Try to click "View All Reviews" if exists
                print("No reviews on main page, trying 'View All Reviews' link")
                try:
                    view_all_buttons = [
                        'button:has-text("View All Reviews")',
                        'button:has-text("Show More Reviews")',
                        'a:has-text("View All")',
                        'div.showMoreButton',
                        'button.show-more'
                    ]
                    
                    for button_sel in view_all_buttons:
                        try:
                            view_all_btn = page.locator(button_sel).first
                            if view_all_btn.count() > 0:
                                view_all_btn.click()
                                page.wait_for_load_state('domcontentloaded')
                                time.sleep(3)
                                print(f"Clicked {button_sel}")
                                break
                        except:
                            continue
                except Exception as e:
                    print(f"Could not navigate to reviews page: {e}")
            
            # Extract reviews
            try:
                # Wait for reviews to load
                page.wait_for_selector('div.user-review, div.review, div.userReview, div[class*="review"]', timeout=15000)
                
                # Get review elements - Myntra has different structures
                review_selectors = [
                    'div.user-review',
                    'div.review',
                    'div.userReview',
                    'div[class*="review"]',
                    'div.index-review',
                    'div.reviews-list div.review'
                ]
                
                review_elements = None
                for sel in review_selectors:
                    try:
                        elements = page.locator(sel)
                        if elements.count() > 0:
                            review_elements = elements.all()
                            print(f"Found {len(review_elements)} review elements using {sel}")
                            break
                    except:
                        continue
                
                if review_elements:
                    for idx, el in enumerate(review_elements[:10]):  # Get first 10
                        try:
                            # Get review text
                            text = ""
                            text_selectors = [
                                'div.review-content, div.review-text, div.review-desc, div.feedback, p.review-desc'
                            ]
                            
                            for text_sel in text_selectors:
                                try:
                                    text_el = el.locator(text_sel).first
                                    if text_el.count() > 0:
                                        text = text_el.inner_text(timeout=3000).strip()
                                        if text:
                                            break
                                except:
                                    continue
                            
                            # Get star rating (Myntra uses filled stars)
                            stars = 0
                            star_selectors = [
                                'div.rating-stars, div.star-container, div.ratings, span.stars'
                            ]
                            
                            for star_sel in star_selectors:
                                try:
                                    star_el = el.locator(star_sel).first
                                    if star_el.count() > 0:
                                        # Check for filled stars
                                        filled_stars = star_el.locator('svg[fill*="#"], span.filled, div.filled').all()
                                        if filled_stars:
                                            stars = len(filled_stars)
                                        else:
                                            # Try to extract from text
                                            star_text = star_el.inner_text(timeout=2000)
                                            import re
                                            numbers = re.findall(r'(\d+)', star_text)
                                            if numbers:
                                                stars = int(numbers[0])
                                        break
                                except:
                                    continue
                            
                            # If stars not found, try to extract from overall element
                            if stars == 0:
                                try:
                                    rating_el = el.locator('div[class*="rating"]').first
                                    if rating_el.count() > 0:
                                        rating_text = rating_el.inner_text(timeout=2000)
                                        import re
                                        numbers = re.findall(r'(\d+)', rating_text)
                                        if numbers:
                                            stars = int(numbers[0])
                                except:
                                    pass
                            
                            if len(text) > 0:
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