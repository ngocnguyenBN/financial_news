import time
from datetime import timedelta, datetime
import requests


def fetch_icb_list():
    icb_api_list = "https://fwtapi2.fialda.com/api/services/app/ICB/GetIcbTree"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
    }

    response = requests.get(icb_api_list, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch ICB list: {response.status_code}")

    list_data = response.json()
    if not list_data.get("success"):
        raise Exception("Failed to retrieve ICB data from API response.")

    icb_data = list_data.get("result", [])
    icb_dict = {}

    def extract_icb_codes(items):
        for item in items:
            icb_dict[item["icbCode"]] = item["icbName"]
            if "childs" in item and item["childs"]:
                extract_icb_codes(item["childs"])

    extract_icb_codes(icb_data)

    return icb_dict


def fetch_icb_fluctuation(
    icb_codes_list="0001,1000,2000,3000,4000,5000,6000,7000,8000,9000",
):
    """
    Fetches the fluctuation data for a list of ICB codes.
    :param icb_codes_list: Comma-separated string of ICB codes (default is all sectors).
    :return: List of fluctuation data for the specified ICB codes.
    """
    icb_api_fluctuation = f"https://fwtapi2.fialda.com/api/services/app/Market/GetICBInfos?icbCode={icb_codes_list}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
    }

    response = requests.get(icb_api_fluctuation, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch ICB fluctuation data: {response.status_code}")

    fluctuation_data = response.json()
    if not fluctuation_data.get("success"):
        raise Exception("Failed to retrieve ICB fluctuation data from API response.")

    return fluctuation_data.get("result", [])
