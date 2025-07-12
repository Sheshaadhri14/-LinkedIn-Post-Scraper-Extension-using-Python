import streamlit as st
import json
import pandas as pd
import time
from selenium import webdriver
from scraper import login_with_cookie, scroll_to_bottom, scrape_posts

# ------------------------ UI Header ------------------------ #
st.set_page_config(page_title="LinkedIn Post Scraper", layout="wide")
st.title("🔍 LinkedIn Filtered Post Scraper")

# ------------------------ Inputs ------------------------ #
cookie_input = st.text_area("🔐 Paste your LinkedIn session cookies (JSON format)", height=200)

keyword = st.text_input("🔤 Keyword or Hashtag", value="hiring")

date_filter = st.selectbox("📅 Date Range", ["", "past-24h", "past-week", "past-month"])

post_type = st.selectbox("🧩 Post Type Filter (optional)", ["", "text", "image", "video", "article", "poll"])

def build_linkedin_search_url(keyword, date_filter):
    base = "https://www.linkedin.com/search/results/content/?"
    filters = f"keywords={keyword}&origin=SWITCH_SEARCH_VERTICAL"
    if date_filter:
        filters += f"&datePosted=\"{date_filter}\""
    return base + filters

# ------------------------ Scraping Trigger ------------------------ #
if st.button("🚀 Start Scraping"):
    try:
        st.info("⏳ Launching browser...")
        options = webdriver.ChromeOptions()
        # comment out the next line to watch browser
        # options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=options)

        cookies = json.loads(cookie_input)
        login_with_cookie(driver, cookies)

        search_url = build_linkedin_search_url(keyword, date_filter)
        st.markdown(f"🔗 **Search URL**: [{search_url}]({search_url})")

        driver.get(search_url)
        time.sleep(2)

        st.info("📜 Scrolling through posts...")
        scroll_to_bottom(driver, scroll_count=8)

        st.info("🔍 Extracting posts...")
        posts = scrape_posts(driver, keyword, post_type)

        if posts:
            df = pd.DataFrame(posts)
            st.success(f"✅ Found {len(df)} matching posts.")
            st.dataframe(df, use_container_width=True)
            st.download_button("⬇️ Download CSV", df.to_csv(index=False), "linkedin_posts.csv")
            st.download_button("⬇️ Download JSON", df.to_json(orient="records"), "linkedin_posts.json")
        else:
            st.warning("⚠️ No posts matched the filters.")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    finally:
        driver.quit()
