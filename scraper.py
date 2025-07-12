import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def login_with_cookie(driver, cookie_dict):
    driver.get("https://www.linkedin.com/")
    for cookie in cookie_dict:
        driver.add_cookie(cookie)
    driver.get("https://www.linkedin.com/feed/")
    time.sleep(3)

def scroll_to_bottom(driver, scroll_count=10):
    for _ in range(scroll_count):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

def scrape_posts(driver, keyword, post_type_filter):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    posts = []

    for post_div in soup.find_all("div", {"data-urn": True, "role": "article"}):
        text = post_div.get_text(separator="\n").strip()
        if not text:
            continue

        # Filter by keyword
        if keyword.lower() not in text.lower():
            continue

        # Filter by post type
        if post_type_filter:
            type_keywords = {
                "text": [],
                "image": [".jpg", ".png", "img", "📷"],
                "video": ["▶", "video", ".mp4"],
                "article": ["Read more", "article", "blog"],
                "poll": ["Vote", "Poll", "Options"]
            }
            tokens = type_keywords.get(post_type_filter.lower(), [])
            if tokens and not any(tok.lower() in text.lower() for tok in tokens):
                continue

        # Try to find the post link
        link_tag = post_div.find("a", href=True)
        link = "https://www.linkedin.com" + link_tag['href'] if link_tag else ""

        posts.append({
            "content": text[:500],
            "link": link
        })

    return posts
