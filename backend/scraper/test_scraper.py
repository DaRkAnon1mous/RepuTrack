# backend/test_scraper.py
from scraper.amazon_scraper import scrape_amazon_reviews
from scraper.flipkart_scraper import scrape_flipkart_reviews
from scraper.meesho_scraper import scrape_meesho_reviews
# from scraper.myntra_scraper import scrape_myntra_reviews

# Your exact links (cleaned for testing)
amazon_url = "https://www.amazon.in/KTM-Black-Booking-Ex-Showroom-Price/dp/B0F539PWVM/?_encoding=UTF8&ref_=pd_hp_d_btf_ls_gwc_pc_en4_"
flipkart_url = "https://www.flipkart.com/boat-airdopes-161-163-asap-charge-40-h-battery-stream-ad-free-music-via-app-support-bluetooth/p/itm6f75fe2fd7c7d"
meesho_url = "https://www.meesho.com/airpod-pro-a-true-wireless-bluetooth-headphone-and-earphone/p/6wayy6"
myntra_url = "https://www.myntra.com/shirts/encore+by+invictus/encore-by-invictus-men-original-fit-solid-spread-collar-cotton-casual-shirt/37396831/buy"
# Test with headless=False first to debug (see browser)
print("Testing Amazon (headless=False for debug):")
amazon_result = scrape_amazon_reviews(amazon_url, headless=False)
print(amazon_result)

# print("\nTesting Flipkart (headless=False for debug):")
# flipkart_result = scrape_flipkart_reviews(flipkart_url, headless=False)
# print(flipkart_result)

# print("Testing Myntra :")
# amazon_result = scrape_myntra_reviews(myntra_url,headless=False)
# print(amazon_result)

# print("Testing Meesho :")
# amazon_result = scrape_meesho_reviews(meesho_url,headless=False)
# print(amazon_result)