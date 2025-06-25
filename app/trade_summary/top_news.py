from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup, Tag
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse
import json

BASE_URL = "https://fwt.fialda.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
}


def fetch_top_news():
    """
    Fetches the top news articles from the Fialda API.
    :return: List of top news articles.
    """
    hot_news_api = "https://fwtapi2.fialda.com/api/services/app/News/GetHotNewsByCategory?category=mostpopular&numberOfItem=6"

    latest_news_api = "https://fwtapi1.fialda.com/api/services/app/Home/GetLatestNews?pageNumber=1&pageSize=100"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
    }

    response_hot_news = requests.get(hot_news_api, headers=headers)

    if response_hot_news.status_code != 200:
        raise Exception(f"Failed to fetch top news: {response_hot_news.status_code}")

    data_hot_news = response_hot_news.json()
    if not data_hot_news.get("success"):
        raise Exception("Failed to retrieve top news from API response.")

    response_latest_news = requests.get(latest_news_api, headers=headers)

    if response_latest_news.status_code != 200:
        raise Exception(
            f"Failed to fetch latest news: {response_latest_news.status_code}"
        )

    data_latest_news = response_latest_news.json()
    if not data_latest_news.get("success"):
        raise Exception("Failed to retrieve latest news from API response.")

    hot_items = data_hot_news.get("result", [])
    latest_items = data_latest_news.get("result", {}).get("items", [])

    # result = {
    #     "time": datetime.now().isoformat(),
    #     "data": hot_items + latest_items,
    # }

    return hot_items + latest_items


def fetch_top_news_with_date(date_news=datetime.now().date(), type_news="stock"):
    if isinstance(date_news, str):
        date_news = datetime.strptime(date_news, "%Y-%m-%d").date()
    url = f"https://fwt.fialda.com/news/{type_news}"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )
    driver.get(url)
    wait = WebDriverWait(driver, 15)

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.ant-modal-content > button")
        )
    )

    time.sleep(5)

    try:
        close_btn = driver.find_element(
            By.CSS_SELECTOR, "div.ant-modal-content > button"
        )
        close_btn.click()
    except NoSuchElementException:
        pass

    wait.until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "ReactVirtualized__Grid__innerScrollContainer")
        )
    )

    scrollable_div = driver.find_element(
        By.CLASS_NAME, "ReactVirtualized__Grid__innerScrollContainer"
    )
    results = []
    seen_urls = set()

    previous_items = -1
    same_count = 0
    max_scrolls = 50
    scroll_position = 0
    step = 300
    for _ in range(max_scrolls):
        driver.execute_script(
            "arguments[0].scrollTop = arguments[1]", scrollable_div, scroll_position
        )
        time.sleep(1.5)
        scroll_position += step

        soup = BeautifulSoup(driver.page_source, "html.parser")
        rows = soup.select(
            "div.ReactVirtualized__Grid__innerScrollContainer > div.table_row"
        )
        if len(rows) == previous_items:
            same_count += 1
            if same_count >= 3:
                break
        else:
            same_count = 0
            previous_items = len(rows)

        for row in rows:
            news_item = row.select_one("a")
            url = news_item["href"] if news_item else None
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            full_url = BASE_URL + url if url.startswith("/") else url

            title = row.select_one(".news-item-title")
            title = title.text.strip() if title else ""

            desc = row.select_one(".des .LinesEllipsis")
            desc = desc.text.strip() if desc else ""

            source = row.select_one(".news-item-soure")
            source = source.text.strip() if source else ""

            datetime_text = row.select_one(".news-item-date")
            if not datetime_text:
                continue
            date_text = " ".join(datetime_text.text.split())

            try:
                dt = datetime.strptime(date_text.strip(), "%d/%m/%Y %H:%M")
            except:
                continue

            if dt.date() < date_news:
                driver.quit()
                return results

            image_style = row.select_one(".news-item-image > div")["style"]
            img_match = re.search(r'url\("(.+?)"\)', image_style)
            image_url = img_match.group(1) if img_match else ""

            # Crawl detail content
            html_content = None
            detail_resp = requests.get(full_url, headers=headers)
            if detail_resp.status_code == 200:
                detail_soup = BeautifulSoup(detail_resp.content, "html.parser")
                html_block = detail_soup.find("div", class_="content-seo")
                if html_block:
                    filtered_html = [
                        p
                        for p in html_block.find_all("p")
                        if isinstance(p, Tag) and not p.find("a")
                    ]
                    raw_text = "\n".join(
                        [p.get_text(strip=True) for p in filtered_html]
                    )
                    html_content = " ".join(raw_text.split())

            symbol_data = []
            list_symbols = row.find("div", class_="list-symbols")
            if list_symbols:
                for a_tag in list_symbols.find_all("a", class_="text-bold"):
                    name_div = a_tag.find("div", class_="name")
                    last_div = a_tag.find("div", class_="last")
                    change_percent_div = a_tag.find("div", class_="changePercent")
                    change_div = a_tag.find("div", class_="change")

                    symbol_info = {
                        "symbol": name_div.text.strip() if name_div else None,
                        "price": float(last_div.text.strip()) if last_div else None,
                        "changePercent": (
                            float(change_percent_div.text.strip())
                            if change_percent_div
                            else None
                        ),
                        "change": change_div.text.strip() if change_div else None,
                    }

                    symbol_data.append(symbol_info)

            results.append(
                {
                    "title": title,
                    "short_description": desc,
                    "source": source,
                    "time": dt,
                    "url": url,
                    "image": image_url,
                    "symbols": symbol_data,
                    "html_content": html_content,
                }
            )

    driver.quit()
    return results


a = fetch_top_news_with_date()
