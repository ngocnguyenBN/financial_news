import requests


def fetch_top_netforeign():
    api = "https://fwtapi1.fialda.com/api/services/app/Stock/GetMarketAnalysises"

    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}

    payload = [
        {"text": "NETFOREIGN_HSX_HNX_UPCOM_VOL_1D_BUY", "cachedTime": None},
        {"text": "NETFOREIGN_HSX_HNX_UPCOM_VOL_1D_SALE", "cachedTime": None},
        {"text": "CHANGEPERCENT_HSX_HNX_UPCOM_1M", "cachedTime": None},
        {"text": "CASHDIVIDENDYIELD_CURRENTPRICE", "cachedTime": None},
    ]

    response = requests.post(api, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch top Net Foreign: {response.status_code}")

    data = response.json()
    if not data.get("success"):
        raise Exception("Failed to retrieve top Net Foreign from API response.")

    return data.get("result", [])
