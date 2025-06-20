import requests


def fetch_khoi_tu_doanh(codesource="VNINDEX", period="1W"):
    """
    Fetches the 'Khoi Tu Doanh' data for a given source.
    :param codesource: The source code for the data (default is 'VNINDEX').
    :return: List of 'Khoi Tu Doanh' data.
    """
    api = f"https://fwtapi2.fialda.com/api/services/app/Market/GetTuDoanhByPeriod?period={period}"

    url = f"{api}&basket={codesource}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch Khoi Tu Doanh data: {response.status_code}")

    data = response.json()
    if not data.get("success"):
        raise Exception("Failed to retrieve Khoi Tu Doanh data from API response.")

    return data.get("result", [])


def get_data_khoi_tu_doanh(period="1W"):
    try:
        list_codes = ["VNINDEX", "HNXINDEX", "UPINDEX"]
        result = {}

        for code in list_codes:
            data = fetch_khoi_tu_doanh(code, period=period)

            result[code] = {"data": data}

        return {"source": "Khoi Tu Doanh", "period": period, "data": result}

    except Exception as e:
        return {"error": str(e)}
