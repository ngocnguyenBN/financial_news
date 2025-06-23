import time
from datetime import timedelta, datetime
import requests


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
