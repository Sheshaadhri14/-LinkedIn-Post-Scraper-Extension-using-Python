import time
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from dateutil import parser

def login_with_cookie(driver, cookie_dict):
    driver.get("https://www.linkedin.com/")
    for cookie in cookie_dict:
        driver.add_cookie(cookie)
    driver.get("https://www.linkedin.com/feed/")
    time.sleep(3)

def login_manually(driver, username, password):
    driver.get("https://www.linkedin.com/login")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)  # Allow time for 2FA or redirects
    except Exception as e:
        raise Exception(f"Manual login failed: {str(e)}")

def scroll_to_bottom(driver, max_scrolls=50):
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0
    while scrolls < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scrolls += 1
    return scrolls

def expand_see_more(driver):
    try:
        see_more_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '...see more') or contains(text(), 'See more')]")
        for btn in see_more_buttons:
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.3)
            except:
                continue
        return len(see_more_buttons)
    except:
        return 0

def scrape_posts(driver, keyword, post_type_filter):
    see_more_count = expand_see_more(driver)
    print(f"Clicked {see_more_count} 'see more' buttons.")  # Debug log
    time.sleep(2)  # Extra wait for dynamic content
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    posts = []

    post_divs = soup.find_all("div", {"data-urn": True})
    print(f"Found {len(post_divs)} potential post elements.")  # Debug log

    for i, post_div in enumerate(post_divs[:5]):  # Log HTML for first 5 posts
        print(f"Post {i+1} HTML: {str(post_div)[:500]}...")  # Debug log (truncated)

    for post_div in post_divs:
        text = post_div.get_text(separator="\n").strip()
        if not text:
            continue

        # Filter by keyword (case-insensitive)
        if keyword and keyword.lower() not in text.lower():
            continue

        # Determine post type
        post_type = "text"
        if post_div.find("img", src=lambda x: x and ("media.licdn.com" in x and "profile-displayphoto" not in x)):
            post_type = "image"
        elif post_div.find("video"):
            post_type = "video"
        elif post_div.find("a", href=lambda x: x and ("article" in x or "blog" in x)):
            post_type = "article"
        elif post_div.find("div", class_=lambda x: x and "poll" in x.lower()):
            post_type = "poll"

        # Filter by post type
        if post_type_filter and post_type_filter.lower() != post_type:
            continue

        # Post ID and Link
        urn = post_div.get("data-urn", "")
        post_id = ""
        post_link = ""
        match = re.search(r'urn:li:activity:(\d+)', urn)
        if match:
            post_id = match.group(1)
            post_link = f"https://www.linkedin.com/feed/update/urn:li:activity:{post_id}"

        # Author Details
        author_name = ""
        author_job_title = ""
        author_profile = ""
        author_elem = post_div.find("span", class_=lambda x: x and "feed-shared-actor__name" in x)
        if author_elem:
            author_name = author_elem.get_text(strip=True)
        job_elem = post_div.find("span", class_=lambda x: x and "feed-shared-actor__description" in x)
        if job_elem:
            author_job_title = job_elem.get_text(strip=True)
        profile_elem = post_div.find("a", href=lambda x: x and "linkedin.com/in/" in x)
        if profile_elem:
            author_profile = profile_elem.get("href")

        # Posted Date (try multiple selectors)
        posted = ""
        # Try multiple possible classes for timestamp
        time_selectors = [
            ("span", lambda x: x and "feed-shared-actor__sub-description" in x),
            ("span", lambda x: x and "feed-shared-actor__sub-title" in x),
            ("time", None),  # Try <time> tag
            ("span", lambda x: x and "social-details-social-counts" in x)
        ]
        for tag, class_fn in time_selectors:
            time_elem = post_div.find(tag, class_=class_fn)
            if time_elem:
                posted = time_elem.get_text(strip=True)
                break
        if posted:
            try:
                # Parse relative dates like "2h ago" or absolute dates
                posted_date = parser.parse(posted, fuzzy=True, default=datetime.now())
                posted = posted_date.strftime("%Y-%m-%d %H:%M:%S")
            except:
                print(f"Failed to parse date: {posted}")  # Log raw date
        else:
            print("No date element found for post.")  # Debug log

        # Media Links
        media_links = []
        for img in post_div.find_all("img"):
            src = img.get("src", "")
            if "media.licdn.com" in src and "profile-displayphoto" not in src:
                media_links.append(src)
        for vid in post_div.find_all("video"):
            src = vid.get("src")
            if src:
                media_links.append(src)

        # Likes, Comments, Shares
        likes = comments = shares = ""
        counts = post_div.find_all("span", class_=lambda x: x and "social-details-social-counts__reactions-count" in x)
        if counts:
            likes = counts[0].get_text(strip=True)
        stats = post_div.find_all("li", class_=lambda x: x and "social-details-social-counts__item" in x)
        if stats:
            if len(stats) >= 2:
                comments = stats[1].get_text(strip=True)
            if len(stats) >= 3:
                shares = stats[2].get_text(strip=True)

        posts.append({
            "content": text,
            "post_type": post_type,
            "media_links": media_links,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "post_link": post_link,
            "post_id": post_id,
            "author_profile": author_profile,
            "posted": posted
        })

    print(f"Collected {len(posts)} posts after filtering.")  # Debug log
    return posts