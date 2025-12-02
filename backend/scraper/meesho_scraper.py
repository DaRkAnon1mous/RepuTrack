# backend/scraper/meesho_scraper.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import random

def scrape_meesho_reviews(url: str, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            # Meesho sometimes blocks based on cookies
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            }
        )
        
        # Anti-detection
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = { runtime: {} };
        """)
        
        page = context.new_page()

        try:
            print(f"Navigating to Meesho: {url}")
            
            # Meesho can be sensitive, add delays
            page.goto(url, timeout=60000, wait_until='domcontentloaded')
            time.sleep(random.uniform(3, 5))
            
            print("Page loaded, extracting data...")
            
            # Extract overall rating
            rating = None
            rating_selectors = [
                'div.rating',
                'div.average-rating',
                'span.rating',
                'div[class*="rating"]',
                'div.rating-container',
                'div.product__rating',
                'div.star-rating'
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
                            # Meesho ratings are usually out of 5
                            if rating > 5:
                                rating = 5.0
                            break
                except Exception as e:
                    print(f"Selector {sel} failed: {e}")
                    continue
            
            print(f"Rating found: {rating}")
            
            # Scroll to reviews section
            try:
                # Meesho reviews section
                reviews_section = page.locator('div.reviews, div.customer-reviews, div.feedback, div.review-section').first
                if reviews_section.count() > 0:
                    reviews_section.scroll_into_view_if_needed(timeout=5000)
                    time.sleep(2)
                else:
                    # Scroll to bottom where reviews usually are
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.7)")
                    time.sleep(2)
            except:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.8)")
                time.sleep(3)
            
            print("Looking for reviews...")
            
            # Check if reviews need to be loaded
            reviews = []
            try:
                # Wait for reviews to appear
                page.wait_for_selector('div.review-card, div.review-item, div.feedback-card, div[class*="review"]', timeout=10000)
                print("Reviews found on main page")
                
            except PlaywrightTimeout:
                # Try to find and click "Load More" or "See All Reviews"
                print("No reviews visible, trying to load more...")
                try:
                    load_more_selectors = [
                        'button:has-text("Load More")',
                        'button:has-text("See More Reviews")',
                        'div.load-more',
                        'button.show-more',
                        'a:has-text("View All Reviews")'
                    ]
                    
                    for btn_sel in load_more_selectors:
                        try:
                            load_btn = page.locator(btn_sel).first
                            if load_btn.count() > 0:
                                load_btn.click()
                                time.sleep(2)
                                page.wait_for_load_state('networkidle', timeout=10000)
                                print(f"Clicked {btn_sel}")
                                break
                        except:
                            continue
                except Exception as e:
                    print(f"Could not load more reviews: {e}")
            
            # Extract reviews
            try:
                # Wait for review cards
                page.wait_for_selector('div.review-card, div.review-item, div.feedback-card, div[class*="review"]', timeout=15000)
                
                # Get review elements
                review_selectors = [
                    'div.review-card',
                    'div.review-item',
                    'div.feedback-card',
                    'div.customer-review',
                    'div[class*="review-card"]',
                    'div[class*="review-item"]'
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
                                'div.review-text',
                                'div.review-content',
                                'div.feedback-text',
                                'div.comment',
                                'p.review-text',
                                'span.review-text'
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
                            
                            # If no specific text element, try getting text from the main element
                            if not text:
                                try:
                                    text = el.inner_text(timeout=3000).strip()
                                    # Remove rating numbers if present
                                    import re
                                    text = re.sub(r'\d+\.?\d*\s*stars?', '', text, flags=re.IGNORECASE)
                                    text = text.strip()
                                except:
                                    pass
                            
                            # Get star rating
                            stars = 0
                            star_selectors = [
                                'div.star-rating',
                                'div.rating-stars',
                                'span.stars',
                                'div[class*="star"]',
                                'div[class*="rating"]'
                            ]
                            
                            for star_sel in star_selectors:
                                try:
                                    star_el = el.locator(star_sel).first
                                    if star_el.count() > 0:
                                        # Check for filled stars (Meesho uses colored stars)
                                        filled_stars = star_el.locator('svg[fill*="#FF"], svg[fill*="#ff"], span.filled, div.active').all()
                                        if filled_stars:
                                            stars = len(filled_stars)
                                        else:
                                            # Try to get from text
                                            star_text = star_el.inner_text(timeout=2000)
                                            import re
                                            numbers = re.findall(r'(\d+)', star_text)
                                            if numbers:
                                                stars = int(numbers[0])
                                        break
                                except:
                                    continue
                            
                            # If stars not found, try pattern matching in the element
                            if stars == 0:
                                try:
                                    element_text = el.inner_text(timeout=2000)
                                    import re
                                    # Look for patterns like "5 stars", "Rating: 4", etc.
                                    star_match = re.search(r'(\d+)\s*stars?|rating\s*:\s*(\d+)', element_text.lower())
                                    if star_match:
                                        stars = int(star_match.group(1) or star_match.group(2))
                                except:
                                    pass
                            
                            if len(text) > 10:  # Minimum text length
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