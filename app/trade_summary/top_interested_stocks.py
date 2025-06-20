import time
from datetime import timedelta, datetime
import requests


def fetch_top_interested_stocks():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
    }
    api = "https://fwtapi1.fialda.com/api/services/app/StatisticalAnalysis/GetTopSymbolInterested?exchanges=HSX,HNX,UPCOM&sortBy=1W"

    response = requests.get(api, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch top interested stocks: {response.status_code}"
        )

    data = response.json()
    if not data.get("success"):
        raise Exception("Failed to retrieve top interested stocks from API response.")

    return data.get("result", [])


# https://fwtapi2.fialda.com/api/services/app/News/GetHotNewsByCategory?category=mostpopular&numberOfItem=6
