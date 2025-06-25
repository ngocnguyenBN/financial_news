from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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
import json


# def fetch_index_fluctuation():
#     """
#     Fetches the index fluctuation data from FireAnt.
#     """
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument("--headless=new")
#     chrome_options.add_argument("--no-sandbox")
#     # chrome_options.add_argument("--start-maximized")
#     chrome_options.add_argument("--window-size=1920,1080")
#     # chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")

#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()),
#         options=chrome_options,
#     )
#     driver.get("https://fireant.vn/dashboard")
#     actions = ActionChains(driver)

#     try:
#         pop_up = driver.find_element(
#             By.CSS_SELECTOR,
#             "body > div.bp5-portal > div > div.bp5-dialog-container.bp5-overlay-content.bp5-overlay-appear-done.bp5-overlay-enter-done > div",
#         )
#         close_button = pop_up.find_element(
#             By.CSS_SELECTOR,
#             "body > div.bp5-portal > div > div.bp5-dialog-container.bp5-overlay-content.bp5-overlay-appear-done.bp5-overlay-enter-done > div > div.bp5-dialog-header > button",
#         )
#         close_button.click()
#     except NoSuchElementException:
#         print("Không có pop-up")

#     try:
#         index_tab = driver.find_element(
#             By.CSS_SELECTOR,
#             "#root > div > div.layout__layout > div:nth-child(11) > div > div.sc-bqMJjo.eQylDP > div > div.sc-cvBxsj.jeDigm.bp5-card > div:nth-child(1) > div > ul > li:nth-child(2)",
#         )

#         index_tab.click()
#         data_all_indices = {}

#         for index_name in ["HSX", "HNX", "UPCOM"]:
#             try:
#                 tab_button = driver.find_element(
#                     By.XPATH,
#                     f"//span[@class='bp5-button-text' and text()='{index_name}']",
#                 )
#                 tab_button.click()
#                 time.sleep(2)

#                 canvas = driver.find_element(
#                     By.CSS_SELECTOR,
#                     "#root > div > div.layout__layout > div:nth-child(11) > div > div.sc-bqMJjo.eQylDP > div > div.sc-cvBxsj.jeDigm.bp5-card > div.sc-frWhYi.VbLZs > div > div > div.echarts-for-react > div:nth-child(1) > canvas",
#                 )
#                 canvas_width = int(canvas.get_attribute("width"))
#                 canvas_height = int(canvas.get_attribute("height"))
#                 data_points = []

#                 for x in range(10, canvas_width - 10, 10):
#                     script = f"""
#                     var canvas = arguments[0];
#                     var rect = canvas.getBoundingClientRect();
#                     var x = {x};
#                     var y = {canvas_height // 2};
#                     var event = new MouseEvent('mousemove', {{
#                         clientX: rect.left + x,
#                         clientY: rect.top + y,
#                         bubbles: true
#                     }});
#                     canvas.dispatchEvent(event);
#                     """
#                     driver.execute_script(script, canvas)
#                     time.sleep(0.1)

#                     try:
#                         tooltip_list = driver.find_elements(
#                             By.CSS_SELECTOR, "div[style*='z-index: 9999999']"
#                         )
#                         for tooltip in tooltip_list:
#                             if tooltip.is_displayed():
#                                 text = tooltip.text.strip()
#                                 if text and text not in data_points:
#                                     # print(f"[{index_name}] x={x} => {text}")
#                                     data_points.append(text)
#                     except Exception:
#                         continue

#                 # Parse tooltip text
#                 parsed_data = []
#                 for item in data_points:
#                     item = item.replace("\n", " ")
#                     try:
#                         ma_ck_part = (
#                             item.split("Mã CK: ")[1].split(" Ảnh hưởng")[0].strip()
#                         )
#                         anh_huong_part = item.split("Ảnh hưởng tới index: ")[1].strip()
#                         parsed_data.append(
#                             {
#                                 "ticker": ma_ck_part,
#                                 "index_affect": float(anh_huong_part),
#                                 "index": index_name,
#                             }
#                         )
#                     except Exception as e:
#                         print(f"Lỗi phân tích chuỗi: {item} - {e}")
#                         continue

#                 data_all_indices[index_name] = parsed_data

#             except NoSuchElementException:
#                 print(f"Không tìm thấy tab: {index_name}")

#         driver.quit()
#     except NoSuchElementException:
#         print("Cannnot find index tab")

#     return data_all_indices


def fetch_index_fluctuation(index_name="UPCOM"):
    """
    Fetches the index fluctuation data from FireAnt for a specific index: HSX, HNX, or UPCOM.
    """
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
    driver.get("https://fireant.vn/dashboard")
    actions = ActionChains(driver)
    time.sleep(2)
    try:
        pop_up = driver.find_element(
            By.CSS_SELECTOR,
            "body > div.bp5-portal > div > div.bp5-dialog-container.bp5-overlay-content.bp5-overlay-appear-done.bp5-overlay-enter-done > div",
        )
        close_button = pop_up.find_element(
            By.CSS_SELECTOR,
            "body > div.bp5-portal > div > div.bp5-dialog-container.bp5-overlay-content.bp5-overlay-appear-done.bp5-overlay-enter-done > div > div.bp5-dialog-header > button",
        )
        close_button.click()
    except NoSuchElementException:
        print("None pop-up")

    try:
        # Bấm tab "Chỉ số"
        # index_tab = driver.find_element(
        #     By.CSS_SELECTOR,
        #     "#root > div > div.layout__layout > div:nth-child(11) > div > div.sc-bqMJjo.eQylDP > div > div.sc-cvBxsj.jeDigm.bp5-card > div:nth-child(1) > div > ul > li:nth-child(2)",
        # )
        index_tab = driver.find_element(
            By.XPATH,
            # "//*[@id='root']/div/div[2]/div[11]/div/div[2]/div/div[1]/div[1]/div/ul/li[2]",
            "//li[@class='bp5-tab' and text()='Tác động tới index']",
        )
        index_tab.click()

        # Bấm chỉ số cụ thể theo tham số
        tab_button = driver.find_element(
            By.XPATH,
            f"//span[@class='bp5-button-text' and text()='{index_name}']",
        )
        tab_button.click()
        time.sleep(5)

        # canvas = driver.find_element(
        #     By.CSS_SELECTOR,
        #     "#root > div > div.layout__layout > div:nth-child(11) > div > div.sc-bqMJjo.eQylDP > div > div.sc-cvBxsj.jeDigm.bp5-card > div.sc-frWhYi.VbLZs > div > div > div.echarts-for-react > div:nth-child(1) > canvas",
        # )
        # canvas = driver.find_element(
        #     By.XPATH,
        #     "//*[@id='root']/div/div[2]/div[11]/div/div[2]/div/div[1]/div[2]/div/div/div[1]/div[1]/canvas",
        # )
        canvas = driver.find_element(
            By.XPATH,
            "//div[@class='echarts-for-react ' and @size-sensor-id='12']//canvas",
        )

        canvas_width = int(canvas.get_attribute("width"))
        canvas_height = int(canvas.get_attribute("height"))
        data_points = []

        for x in range(10, canvas_width - 10, 10):
            script = f"""
            var canvas = arguments[0];
            var rect = canvas.getBoundingClientRect();
            var x = {x};
            var y = {canvas_height // 2};
            var event = new MouseEvent('mousemove', {{
                clientX: rect.left + x,
                clientY: rect.top + y,
                bubbles: true
            }});
            canvas.dispatchEvent(event);
            """
            driver.execute_script(script, canvas)
            time.sleep(0.1)

            try:
                tooltip_list = driver.find_elements(
                    By.CSS_SELECTOR, "div[style*='z-index: 9999999']"
                )
                for tooltip in tooltip_list:
                    if tooltip.is_displayed():
                        text = tooltip.text.strip()
                        if text and text not in data_points:
                            data_points.append(text)
            except Exception:
                continue

        # print(f"Found {len(data_points)} data points for {index_name} index.")
        # Parse tooltip text
        parsed_data = []
        for item in data_points:
            item = item.replace("\n", " ")
            try:
                ma_ck_part = item.split("Mã CK: ")[1].split(" Ảnh hưởng")[0].strip()
                # print(f"Processing ticker: {ma_ck_part}")
                if len(ma_ck_part) > 3:
                    continue
                anh_huong_part = item.split("Ảnh hưởng tới index: ")[1].strip()
                parsed_data.append(
                    {
                        "ticker": ma_ck_part,
                        "index_affect": float(anh_huong_part),
                        "index": index_name,
                    }
                )
            except Exception as e:
                print(f"Error parsing: {item} - {e}")
                continue

        driver.quit()
        return parsed_data

    except NoSuchElementException:
        driver.quit()
        print("No Data")
        return []
