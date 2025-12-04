# backend/test_scraper.py
from scraper.amazon_scraper import scrape_amazon_reviews
from scraper.flipkart_scraper import scrape_flipkart_reviews
# from scraper.meesho_scraper import scrape_meesho_reviews
from scraper.myntra_scraper import scrape_myntra_reviews




# Your exact links (cleaned for testing)
amazon_url = "https://www.amazon.in/KTM-Black-Booking-Ex-Showroom-Price/dp/B0F539PWVM/?_encoding=UTF8&ref_=pd_hp_d_btf_ls_gwc_pc_en4_"
flipkart_url = "https://www.flipkart.com/boat-airdopes-161-163-asap-charge-40-h-battery-stream-ad-free-music-via-app-support-bluetooth/p/itm6f75fe2fd7c7d"
meesho_url = "https://www.meesho.com/infinix-hot-60-6gb-128gb-shadow-blue-5g-smartphone-free-cover-included/p/9en88m"
myntra_url = "https://www.myntra.com/tshirts/xyxx/xyxx-men-solid-slim-fit-polo-collar-pure-cotton-tshirt/35307518/buy"
ajio_url = "https://www.ajio.com/decathlon-wedze--men-warm-winter-headband/p/702373880_grey"


# Test with headless=False first to debug (see browser)
# print("Testing Amazon (headless=False for debug):")
# amazon_result = scrape_amazon_reviews(amazon_url, headless=False)
# print(amazon_result)

# print("\nTesting Flipkart (headless=False for debug):")
# flipkart_result = scrape_flipkart_reviews(flipkart_url, headless=False)
# print(flipkart_result)

# print("Testing Myntra :")
# amazon_result = scrape_myntra_reviews(myntra_url,headless=False)
# print(amazon_result)

# print("Testing Meesho :")
# amazon_result2 = scrape_meesho_reviews(meesho_url,headless=False)
# print(amazon_result2)

print("Testing Ajio :")
amazon_result3 = scrape_ajio_reviews(ajio_url,headless=False)
print(amazon_result3)