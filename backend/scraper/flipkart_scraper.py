# backend/scraper/flipkart_scraper.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import random

def scrape_flipkart_reviews(url: str, headless=True):
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
            
            page.goto(url, timeout=60000, wait_until='domcontentloaded')
            time.sleep(random.uniform(2, 4))
            
            print("Page loaded, closing popups...")
            
            # Close login popup
            try:
                close_btn = page.locator('button._2KpZ6l._2doB4z, button[class*="close"], span._30XB9F, button >> text=/✕|Close/i').first
                if close_btn.count() > 0:
                    close_btn.click(timeout=3000)
                    time.sleep(1)
                    print("Closed popup")
            except:
                print("No popup to close")
            
            # DEBUG: Print page title to confirm we're on the right page
            print(f"Page title: {page.title()}")
            
            # Extract rating with MORE selectors
            rating = None
            rating_selectors = [
                'div._3LWZlK',
                'div.XQDdHH', 
                'div._3LWZlK.FxZV4W',
                'span._1lRcqv',
                'div[class*="gUuXy"]',
                'div >> text=/^[0-9]\.[0-9]★?$/',  # Regex for "4.2★" pattern
            ]
            
            print("Looking for rating...")
            for sel in rating_selectors:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0:
                        text = el.inner_text(timeout=5000).strip()
                        print(f"Found rating with {sel}: {text}")
                        # Extract number
                        import re
                        match = re.search(r'(\d+\.?\d*)', text)
                        if match:
                            rating = float(match.group(1))
                            print(f"Extracted rating: {rating}")
                            break
                except Exception as e:
                    print(f"Selector {sel} failed: {e}")
                    continue
            
            if not rating:
                print("Rating not found, trying alternative method...")
                # Sometimes rating is in a different section
                try:
                    all_text = page.content()
                    import re
                    # Look for pattern like "4.2 out of 5" or just "4.2★"
                    matches = re.findall(r'(\d+\.?\d*)\s*(?:out of 5|★|⭐)', all_text)
                    if matches:
                        rating = float(matches[0])
                        print(f"Found rating from page content: {rating}")
                except:
                    pass
            
            # Scroll to reviews section
            print("Scrolling to reviews...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
            time.sleep(2)
            
            # Try to find and click "All XX reviews" or similar button
            try:
                # Try multiple possible review link texts
                review_link_selectors = [
                    'text=/All.*reviews?/i',
                    'text=/View all.*reviews?/i',
                    'text=/See all.*reviews?/i',
                    'span:has-text("Reviews")',
                    'div:has-text("Reviews")'
                ]
                
                for link_sel in review_link_selectors:
                    try:
                        all_reviews_btn = page.locator(link_sel).first
                        if all_reviews_btn.count() > 0:
                            print(f"Found reviews link with: {link_sel}")
                            all_reviews_btn.click(timeout=5000)
                            time.sleep(2)
                            print("Clicked on reviews link")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"Could not click all reviews: {e}")
            
            # UPDATED: Try many more selector combinations
            reviews = []
            
            review_container_selectors = [
                'div.cPHDOP',           # Old common
                'div._27M-vq',          # Old alternative
                'div.col.JOpGWq',       # 2024 layout
                'div[class*="review"]', # Generic
                'div.RcXBOT',           # New 2025 class
                'div._1PBCrt',          # Another new one
                'div.col._2wzgFH',      # Grid item
                'div.row._2nQjXd',      # Row container
                'div._1AtVbE',          # Common review container
                'div.col-9-12',         # Layout column
            ]
            
            print("Looking for review containers...")
            review_elements = []
            found_selector = None
            
            for container_sel in review_container_selectors:
                try:
                    page.wait_for_selector(container_sel, timeout=8000)
                    elements = page.locator(container_sel).all()
                    
                    # Filter elements that look like reviews (have some text)
                    valid_elements = []
                    for el in elements:
                        try:
                            text = el.inner_text(timeout=2000)
                            if len(text) > 30:  # Reviews usually have substantial text
                                valid_elements.append(el)
                        except:
                            continue
                    
                    if len(valid_elements) > 0:
                        review_elements = valid_elements
                        found_selector = container_sel
                        print(f"Found {len(review_elements)} potential reviews with: {container_sel}")
                        break
                        
                except PlaywrightTimeout:
                    print(f"Selector {container_sel} not found, trying next...")
                    continue
            
            # If still no reviews, try a more generic approach
            if not review_elements:
                print("Trying generic text-based search...")
                try:
                    # Look for specific review text patterns in the page
                    page.wait_for_selector('div', timeout=5000)
                    
                    # Try to find elements with review indicators
                    potential_selectors = [
                        'div:has(svg)', # Divs with star icons
                        'div.row:has-text("★")',
                        'div.row:has-text("Certified Buyer")',
                        'p:has-text("★")',
                    ]
                    
                    for sel in potential_selectors:
                        try:
                            elements = page.locator(sel).all()
                            print(f"Trying selector: {sel}, found {len(elements)} elements")
                            
                            for el in elements[:50]:
                                try:
                                    text = el.inner_text(timeout=1000).strip()
                                    # Reviews typically have: star rating, decent length, not too long
                                    if len(text) > 50 and len(text) < 1500 and ('★' in text or 'Certified Buyer' in text):
                                        review_elements.append(el)
                                        if len(review_elements) >= 10:
                                            break
                                except:
                                    continue
                            
                            if review_elements:
                                print(f"Found {len(review_elements)} reviews with: {sel}")
                                break
                        except Exception as e:
                            print(f"Selector {sel} failed: {e}")
                            continue
                    
                except Exception as e:
                    print(f"Generic search failed: {e}")
            
            if not review_elements:
                print("No reviews found with any method")
                
                # DEBUG: Save page HTML for inspection
                try:
                    html_content = page.content()
                    with open('flipkart_debug.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print("Saved page HTML to flipkart_debug.html for debugging")
                except:
                    pass
                
                browser.close()
                return {"rating": rating, "reviews": []}
            
            # Extract review data
            print(f"Extracting data from {len(review_elements)} review elements...")
            
            for idx, el in enumerate(review_elements[:10]):
                try:
                    full_text = el.inner_text(timeout=3000).strip()
                    
                    # Split by newlines to find actual review text
                    lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                    
                    # Extract star rating from text
                    stars = 5
                    import re
                    star_match = re.search(r'(\d+)★', full_text)
                    if star_match:
                        stars = int(star_match.group(1))
                    
                    # Find the longest line as review text (usually the actual review)
                    text = max(lines, key=len) if lines else full_text
                    
                    # Clean up text (remove rating, dates, etc.)
                    text = re.sub(r'\d+★', '', text)  # Remove star rating
                    text = re.sub(r'\d+ days? ago', '', text)  # Remove date
                    text = re.sub(r'READ MORE', '', text, flags=re.IGNORECASE)
                    text = text.strip()
                    
                    if text and len(text) > 20:
                        reviews.append({"text": text, "stars": stars})
                        print(f"Extracted review {idx + 1}: {stars} stars, {len(text)} chars")
                
                except Exception as e:
                    print(f"Error extracting review {idx + 1}: {e}")
                    continue
            
            browser.close()
            
            result = {"rating": rating, "reviews": reviews}
            print(f"\nFinal result: {len(reviews)} reviews, rating: {rating}")
            return result

        except Exception as e:
            print(f"Error occurred: {e}")
            import traceback
            traceback.print_exc()
            browser.close()
            return {"error": str(e), "rating": None, "reviews": []}