import requests


def fetch_khoi_ngoai(codesource="HNXINDEX", period="1D"):
    """
    Fetches the 'Khoi Ngoai' data for the HNX index.
    :return: List of 'Khoi Ngoai' data.
    """
    convert_period = {
        "1D": "oneDay",
        "1W": "oneWeek",
        "1M": "oneMonth",
        "3M": "threeMonth",
        "6M": "sixMonth",
        "1Y": "oneYear",
    }
    period = convert_period.get(period, "1D")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
    }
    api = f"https://fwtapi2.fialda.com/api/services/app/Home/GetForeignerTradingChart?indexCode={codesource}&chartPedirod={period}"

    response = requests.get(api, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch Khoi Ngoai data: {response.status_code}")

    data = response.json()
    if not data.get("success"):
        raise Exception("Failed to retrieve Khoi Ngoai data from API response.")

    result = data.get("result", {})

    first_volume = result.get("tradingVolumeChart", [None])[0]
    first_value = result.get("tradingValueChart", [None])[0]

    return {
        "tradingVolumeChart_first": first_volume,
        "tradingValueChart_first": first_value,
    }


def get_data_khoi_ngoai(period="1D"):
    try:
        list_codes = ["VNINDEX", "HNXINDEX", "UPINDEX"]
        result = {}

        for code in list_codes:
            data = fetch_khoi_ngoai(code, period)

            result[code] = {"data": data}

        return {"source": "Khoi Ngoai", "data": result}

    except Exception as e:
        return {"error": str(e)}
