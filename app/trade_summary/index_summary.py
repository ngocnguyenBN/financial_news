import requests


def fetch_index_summary():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
    }
    url = "https://iboard-query.ssi.com.vn/exchange-index/multiple"

    payload = {
        "indexIds": ["VNINDEX", "VN30", "HNX30", "VNXALL", "HNXIndex", "HNXUpcomIndex"]
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch index summary: {response.status_code}")

    data = response.json()
    # if not data.get("success"):
    #     raise Exception("Failed to retrieve index summary from API response.")

    return data.get("data", [])
