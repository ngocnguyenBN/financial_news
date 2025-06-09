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

BASE_URL = "https://vietstock.vn"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
}


def parse_time_string(time_str):
    now = datetime.now()

    try:
        if re.match(r"\d{2}/\d{2} \d{2}:\d{2}", time_str):
            time_parsed = datetime.strptime(time_str, "%d/%m %H:%M")
            time_parsed = time_parsed.replace(year=now.year)
            return time_parsed
    except Exception:
        pass

    patterns = {
        "giây": "seconds",
        "phút": "minutes",
        "giờ": "hours",
    }

    for k, v in patterns.items():
        match = re.match(rf"(\d+)\s*{k}\s+trước", time_str)
        if match:
            value = int(match.group(1))
            return now - timedelta(**{v: value})

    return None


def get_vst_news(content):
    new_data = []

    soup = BeautifulSoup(content, "html.parser")
    posts = soup.find_all(
        "div", class_="single_post post_type12 type20 mb20 channelContent"
    )

    for post in posts:
        try:
            meta3 = post.select_one("div.meta3")
            a_tags = meta3.find_all("a") if meta3 else []

            type_info = time_info = None

            if len(a_tags) >= 2:
                type_tag = a_tags[0]
                time_tag = a_tags[1]

                type_info = {
                    "href": type_tag.get("href"),
                    "title": type_tag.get("title"),
                    "text": type_tag.get_text(strip=True),
                }

                time_info = {
                    "href": time_tag.get("href"),
                    "title": time_tag.get("title"),
                    "text": time_tag.get_text(strip=True),
                }

            title_tag = post.select_one("h4 a.fontbold")
            title = title_tag.text.strip() if title_tag else None
            # relative_link = title_tag["href"] if title_tag else None
            # full_link = BASE_URL + relative_link if relative_link else None

            relative_link = title_tag["href"] if title_tag else None
            if relative_link:
                full_link = (
                    relative_link
                    if relative_link.startswith("http")
                    else BASE_URL + relative_link
                )
            else:
                full_link = None

            html_content = None
            if full_link:
                detail_resp = requests.get(full_link, headers=headers)
                if detail_resp.status_code == 200:
                    detail_soup = BeautifulSoup(detail_resp.content, "html.parser")

                    domain = urlparse(full_link).netloc

                    html_content = None

                    if "vietstock.vn" in domain:
                        html_block = detail_soup.find(
                            "div", class_="row scroll-content"
                        )
                    elif "fili.vn" in domain:
                        html_block = detail_soup.find(
                            "div", class_="contentView", itemprop="articleBody"
                        )
                    else:
                        html_block = None

                    if html_block:
                        raw_text = html_block.get_text(separator="\n", strip=True)
                        # html_content = re.sub(r"\n+", "\n", raw_text).strip()
                        html_content = " ".join(raw_text.split())
                    else:
                        html_content = None

            new_data.append(
                {
                    "type_content": type_info["text"] if type_info else None,
                    "time": parse_time_string(time_info["text"]) if time_info else None,
                    "title": title,
                    "link": full_link,
                    "html_content": html_content,
                }
            )

        except Exception as e:
            print("Error:", e)
    return new_data


def fetch_vst_news(date_from="", date_to=""):
    """Fetch news articles from Vietstock within a date range.

    Args:
        date_from (str, optional): The start date for fetching news articles.
        date_to (str, optional): The end date for fetching news articles.

    Returns:
        list: A list of news articles fetched from Vietstock.
    """
    url = "https://vietstock.vn/chung-khoan.htm"

    if not date_to:
        date_to = datetime.now().strftime("%Y-%m-%d")

    # if date_from: empty, default to get news today
    if not date_from:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = get_vst_news(response.content)
        return data
    else:
        try:
            all_data = []
            from_date = datetime.strptime(date_from, "%Y-%m-%d")
            to_date = datetime.strptime(date_to, "%Y-%m-%d")

            current = from_date
            while current < to_date:
                next_day = current + timedelta(days=1)

                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--no-sandbox")
                # chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--window-size=1920,1080")
                # chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument(
                    "--disable-blink-features=AutomationControlled"
                )

                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=chrome_options,
                )

                driver.get(url)

                try:
                    input_element = driver.find_element(
                        By.XPATH,
                        "//*[@id='bg-full-js']/div[1]/div[1]/div[2]/div[1]/div[3]/div[1]/div/input",
                    )
                    driver.execute_script("arguments[0].click();", input_element)

                    input_element.clear()
                    time.sleep(0.2)

                    date_range_str = f"{current.strftime('%Y-%m-%d')} - {next_day.strftime('%Y-%m-%d')}"
                    input_element.send_keys(date_range_str)
                    input_element.send_keys(Keys.ENTER)

                    print(f"Range date: {date_range_str}")
                    time.sleep(3)

                    while True:
                        content = driver.page_source
                        if content:
                            data = get_vst_news(content)
                            all_data.extend(data)
                            print(f"Data for {date_range_str}: {data}")
                        else:
                            print(f"No data found for {date_range_str}")
                        # Check if there is a next page button
                        # and click it if it exists
                        try:
                            next_page_button = driver.find_element(
                                By.XPATH, "//*[@id='page-next ']/a"
                            )
                            if next_page_button.is_displayed():
                                driver.execute_script(
                                    "arguments[0].click();", next_page_button
                                )
                                time.sleep(2)
                            else:
                                break
                        except NoSuchElementException:
                            break

                except Exception as e:
                    print("Error when entering date:", e)

                finally:
                    driver.quit()

                current = next_day
        except ValueError as ve:
            print("❌ Date format error. Correct format is YYYY-MM-DD:", ve)

        return all_data
