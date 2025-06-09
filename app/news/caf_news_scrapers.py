from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from datetime import timedelta, datetime
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse


def scroll_to_bottom(driver, pause_time=1.0, max_attempts=30):
    last_height = driver.execute_script("return document.body.scrollHeight")
    attempts = 0

    while attempts < max_attempts:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(pause_time)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        attempts += 1


def fetch_caf_news(date_from="", date_to=""):
    BASE_URL = "https://cafef.vn"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
    }

    url = "https://cafef.vn/thi-truong-chung-khoan.chn"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )

    driver.get(url)
    scroll_to_bottom(driver)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    containers = soup.find_all("div", class_="listchungkhoannew type-2 loadedStock")

    all_posts = []

    for container in containers:
        posts = container.find_all(
            "div",
            class_=lambda c: c
            and ("tlitem" in c.split() or "box-category-item" in c.split()),
        )
        all_posts.extend(posts)

    unique_posts = {}
    for post in all_posts:
        link_tag = post.find("a")
        href = link_tag["href"] if link_tag and link_tag.has_attr("href") else None
        if href and href not in unique_posts:
            unique_posts[href] = post

    posts = list(unique_posts.values())

    all_data = []
    for post in posts:
        try:
            title_tag = post.find("h3").find("a")
            title = title_tag.get_text(strip=True)
            relative_link = title_tag.get("href")
            full_link = (
                BASE_URL + relative_link
                if relative_link.startswith("/")
                else relative_link
            )

            time_span = post.find("span", class_="time")
            time_text = time_span.get_text(strip=True) if time_span else None
            time_iso = time_span.get("title") if time_span else None

            symbol_tag = post.find("p", class_="top5_news_mack magiaodich")
            if symbol_tag:
                symbol = symbol_tag.get("data-symbol")

                price_tag = symbol_tag.find("span", class_="number1")
                price = price_tag.get_text(strip=True) if price_tag else None

                change_tag = symbol_tag.find("span", class_="number2")
                if change_tag:
                    raw_change = change_tag.get_text(strip=True)
                    if " " in raw_change and "(" in raw_change:
                        change, _, percent = raw_change.partition(" (")
                        percent_change = percent.rstrip(")")
                    else:
                        change = raw_change
                        percent_change = None
                else:
                    change = percent_change = None
            else:
                symbol = None
                price = None
                change = None
                percent_change = None

            description_tag = post.find("p", class_="sapo box-category-sapo")
            description = (
                description_tag.get_text(strip=True) if description_tag else None
            )

            html_content = None
            if full_link:
                detail_resp = requests.get(full_link, headers=headers)
                if detail_resp.status_code == 200:
                    detail_soup = BeautifulSoup(detail_resp.content, "html.parser")

                    domain = urlparse(full_link).netloc

                    html_content = None

                    if "cafef.vn" in domain:
                        html_block = detail_soup.find("div", class_="contentdetail")
                    else:
                        html_block = None
                    if html_block:
                        raw_text = html_block.get_text(separator="\n", strip=True)
                        html_content = " ".join(raw_text.split())
                    else:
                        html_content = None
            data = {
                "title": title,
                "symbol": symbol,
                "price": price,
                "change": change,
                "percent_change": percent_change,
                "link": full_link,
                "time": time_iso,
                "html_content": html_content,
            }

            print(data)
            all_data.append(data)

        except Exception as e:
            print("Error:", e)

    driver.quit()

    final_data = []
    if date_from == "" and date_to == "":
        return all_data
    else:
        try:
            from_date = (
                datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None
            )
            to_date = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None
        except ValueError:
            from_date = to_date = None

        for item in all_data:
            if isinstance(item["time"], str):
                try:
                    article_date = datetime.fromisoformat(item["time"]).date()
                    if from_date and to_date:
                        if from_date <= article_date <= to_date:
                            final_data.append(item)
                    elif from_date:
                        if article_date >= from_date:
                            final_data.append(item)
                    elif to_date:
                        if article_date <= to_date:
                            final_data.append(item)
                    else:
                        if article_date == datetime.now().date():
                            final_data.append(item)
                except ValueError:
                    continue
        return final_data
