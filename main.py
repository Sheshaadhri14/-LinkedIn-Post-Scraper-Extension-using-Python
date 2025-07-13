import streamlit as st
import json
import pandas as pd
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper import login_with_cookie, login_manually, scroll_to_bottom, scrape_posts

# ------------------------ UI Header ------------------------ #
st.set_page_config(page_title="LinkedIn Post Scraper", layout="wide")
st.title("🔍 LinkedIn Filtered Post Scraper")

# ------------------------ Inputs ------------------------ #
auth_method = st.selectbox("🔐 Authentication Method", ["Session Cookies", "Manual Login"])

if auth_method == "Session Cookies":
    cookie_input = st.text_area("Paste your LinkedIn session cookies (JSON format)", height=200)
else:
    username = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")

scrape_target = st.selectbox("🎯 Scrape Target", ["Feed", "Profile", "Page", "Group"])
target_url = st.text_input("🔗 Target URL (for Profile/Page/Group)", placeholder="e.g., https://www.linkedin.com/in/username/")

keyword = st.text_input("🔤 Keyword or Hashtag", value="hiring")

date_filter = st.selectbox("📅 Date Range", ["past-24h", "past-week", "past-month", "any-time"])

st.subheader("📅 Optional Custom Date Range Filter")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date (optional)", value=None, min_value=datetime(2000, 1, 1))
with col2:
    end_date = st.date_input("End Date (optional)", value=None)

post_type = st.selectbox("🧩 Post Type Filter (optional)", ["", "text", "image", "video", "article", "poll"])

# ------------------------ Dynamic Filter for Results ------------------------ #
#'''if "posts_df" in st.session_state:
 #   st.subheader("🔎 Filter Results")
  #  filter_keyword = st.text_input("Filter by keyword in content")
   # filter_post_type = st.selectbox("Filter by post type", ["", "text", "image", "video", "article", "poll"], key="filter_post_type")
    #if st.button("Apply Filters"):
     #   df = st.session_state.posts_df
      #  if filter_keyword:
       #     df = df[df["content"].str.contains(filter_keyword, case=False, na=False)]
        ##   df = df[df["post_type"] == filter_post_type]
        #st.dataframe(df[["author_name", "author_job_title", "posted", "likes", "comments", "content", "post_link"]], use_container_width=True)
#'''
# ------------------------ Scraping Trigger ------------------------ #
if st.button("🚀 Start Scraping"):
    try:
        st.info("⏳ Launching browser...")
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless=new")  # Uncomment to run headlessly
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=options)

        try:
            st.info("🔐 Authenticating...")
            if auth_method == "Session Cookies":
                cookies = json.loads(cookie_input)
                if not isinstance(cookies, list):
                    raise ValueError("Cookies must be a list of dictionaries.")
                login_with_cookie(driver, cookies)
            else:
                login_manually(driver, username, password)
            
            # Verify login success
            driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            if "login" in driver.current_url:
                raise Exception("Login failed. Check credentials or CAPTCHA.")
            st.info("✅ Login successful.")

        except Exception as e:
            st.error(f"❌ Authentication error: {str(e)}")
            driver.quit()
            st.stop()

        if scrape_target == "Feed":
            base = "https://www.linkedin.com/search/results/content/?"
            filters = f"keywords={keyword}&origin=SWITCH_SEARCH_VERTICAL&datePosted={date_filter}"
            search_url = base + filters
        else:
            search_url = target_url or "https://www.linkedin.com/feed/"
            if not search_url.startswith("https://www.linkedin.com"):
                st.error("❌ Invalid target URL. Must start with https://www.linkedin.com")
                driver.quit()
                st.stop()

        st.markdown(f"🔗 **Search URL**: [{search_url}]({search_url})")
        driver.get(search_url)
        time.sleep(3)

        # Check if the page loaded correctly
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            if "search/results" in search_url and "no results found" in driver.page_source.lower():
                st.warning("⚠️ No results found for the search query. Try a different keyword or date range.")
                driver.quit()
                st.stop()
        except:
            st.error("❌ Failed to load the search page. Check URL or network.")
            driver.quit()
            st.stop()

        st.info("📜 Scrolling through posts...")
        scroll_count = scroll_to_bottom(driver)
        st.info(f"🔄 Performed {scroll_count} scrolls.")

        st.info("🔍 Extracting posts...")
        posts = scrape_posts(driver, keyword, post_type)
        st.info(f"📋 Found {len(posts)} posts before filtering.")

        if posts:
            df = pd.DataFrame(posts)
            # Convert posted date to datetime for filtering
            df["posted_date"] = pd.to_datetime(df["posted"], errors="coerce")
            # Log unparsed dates
            unparsed = df[df["posted_date"].isna()]["posted"].tolist()
            if unparsed:
                filtered_unparsed = [date for date in unparsed if date.strip()]
            # Apply custom date range filter if provided
            if start_date and end_date:
                start_date = datetime.combine(start_date, datetime.min.time())
                end_date = datetime.combine(end_date, datetime.max.time())
                filtered_df = df[(df["posted_date"] >= start_date) & (df["posted_date"] <= end_date)]
                if len(filtered_df) == 0 and len(unparsed) == len(df):
                    filtered_df = df
                else:
                    df = filtered_df
                    st.info(f"📅 Filtered to {len(df)} posts within custom date range.")
            st.session_state.posts_df = df
            display_cols = ["posted", "likes", "comments", "content", "post_link"]
            existing_cols = [col for col in display_cols if col in df.columns]
            if len(df) > 0:
                st.success(f"✅ Found {len(df)} matching posts after filtering.")
                st.dataframe(df[existing_cols], use_container_width=True)
                st.download_button("⬇️ Download CSV", df.to_csv(index=False), "linkedin_posts.csv")
                st.download_button("⬇️ Download JSON", df.to_json(orient="records"), "linkedin_posts.json")
            else:
                st.warning("⚠️ No posts matched the filters (keyword, post type, or custom date range).")
        else:
            st.warning("⚠️ No posts found. Check keyword, date filter, or target URL.")

    except Exception as e:
        st.exception(f"❌ Error: {str(e)}")

    finally:
        driver.quit()