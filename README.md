Here’s a complete, clean `README.md` for your **LinkedIn Post Scraper** project:

---

````markdown
# 🔍 LinkedIn Filtered Post Scraper (Streamlit + Selenium)

A browser automation tool and Streamlit dashboard that lets you scrape **filtered LinkedIn posts** based on:

- ✅ Keywords or Hashtags
- ✅ Date Filters (`Past 24h`, `Past Week`, `Past Month`)
- ✅ Post Types (`Text`, `Image`, `Video`, `Poll`, `Article`)
- ✅ Your LinkedIn session cookies (no login UI)

---

## 📸 Preview

![LinkedIn Scraper UI Preview](preview.png) <!-- Add a screenshot named preview.png if you want -->

---

## 🚀 Features

- 🔐 Cookie-based session login (no need to store username/password)
- 📤 Export results as **CSV or JSON**
- 🔄 Scrolls to load more posts (handles infinite scroll)
- 🧠 Smart filters for post type based on content
- 💻 Uses Selenium + BeautifulSoup for dynamic scraping
- 📊 Streamlit frontend with live filtering and download options

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/linkedin-post-scraper.git
cd linkedin-post-scraper

# Install required libraries
pip install -r requirements.txt

# OR install individually
pip install streamlit selenium beautifulsoup4 pandas
````

---

## 🧰 Setup ChromeDriver

1. Download [ChromeDriver](https://chromedriver.chromium.org/downloads) matching your Chrome version.
2. Place `chromedriver` in the project root or your system PATH.

---

## 🏁 Run the App

```bash
streamlit run main.py
```

---

## ✍️ How to Use

### 1. 🔐 Get Your LinkedIn Session Cookie (`li_at`)

1. Open `https://www.linkedin.com` in Chrome
2. Press `F12` to open DevTools → Go to **Application** tab
3. Under `Cookies → https://www.linkedin.com`, find the cookie named `li_at`
4. Paste it in the app as:

```json
[
  {
    "name": "li_at",
    "value": "your_li_at_cookie_here",
    "domain": ".linkedin.com"
  }
]
```

### 2. 🧾 Provide Filter Inputs

* **Keyword**: e.g. `hiring`, `#frontend`
* **Date Range**: `past-24h`, `past-week`, `past-month`
* **Post Type**: Choose from dropdown

### 3. 📊 View + Export Results

* View matching posts in a table
* Download CSV or JSON instantly

---

## 📝 Project Structure

```text
├── main.py          # Streamlit app and UI
├── scraper.py       # All scraping logic (Selenium + BeautifulSoup)
├── requirements.txt
├── README.md
```

---

## 🔒 Disclaimer

This tool is for **educational/personal use only**. Scraping LinkedIn content may violate their [Terms of Service](https://www.linkedin.com/legal/user-agreement). Use responsibly.

---
OUPUT PREVIEW:
<img width="1894" height="774" alt="image" src="https://github.com/user-attachments/assets/5515e0ab-9acf-41ab-83b9-84c0bb414429" />


