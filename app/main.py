# app/main.py
from fastapi import FastAPI, Query
from typing import Optional
from news.vnb_news_scraper import fetch_vnb_news
from news.vst_news_scraper import fetch_vst_news
from news.caf_news_scrapers import fetch_caf_news

from datetime import datetime, timedelta

app = FastAPI()


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


@app.get("/vietnambiz")
def get_vnb_news(start: Optional[str] = Query(None), end: Optional[str] = Query(None)):
    """
    start & end format: yyyy-mm-dd (ISO format)
    """
    results = []
    if start and end:
        try:
            # Parse input as yyyy-mm-dd
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            for single_date in daterange(start_dt, end_dt):
                date_str = single_date.strftime("%d-%m-%Y")
                results.extend(fetch_vnb_news(date_str))
        except ValueError:
            return {"error": "Invalid date format. Use yyyy-mm-dd."}
    else:
        results = fetch_vnb_news()

    return {"source": "Vietnambiz", "articles": results}


@app.get("/vietstock")
def get_vst_news(start: Optional[str] = Query(None), end: Optional[str] = Query(None)):
    """
    start & end format: YYYY-MM-DD
    """
    try:
        if start and end:
            news = fetch_vst_news(start, end)
        else:
            news = fetch_vst_news()

        return {"source": "Vietstock", "articles": news}
    except Exception as e:
        return {"error": str(e)}


@app.get("/cafef")
def get_cafef_news(
    start: Optional[str] = Query(None), end: Optional[str] = Query(None)
):
    """
    Fetch today's stock market news from Cafef.
    """
    try:
        if start and end:
            news = fetch_caf_news(start, end)
        else:
            news = fetch_caf_news()
        return {"source": "Cafef", "articles": news}
    except Exception as e:
        return {"error": str(e)}


@app.get("/top_sectors")
def get_top_sectors(interval: str = Query("1D", regex="^(1D|1W|1M|3M|6M|1Y|YTD)$")):
    """
    Fetch top sectors data, filter key fields, and sort by changePercent descending.
    """
    from trade_summary.top_sectors import fetch_icb_fluctuation

    try:
        icb_codes_list = "0001,1000,2000,3000,4000,5000,6000,7000,8000,9000"
        fluctuation_data = fetch_icb_fluctuation(icb_codes_list)

        percent_field = f"changePercent{interval}"

        filtered_data = []
        for item in fluctuation_data:
            change_percent = item.get(percent_field)
            if change_percent is not None:
                filtered_data.append(
                    {
                        "id": item.get("id"),
                        "icbCode": item.get("icbCode"),
                        "icbName": item.get("icbName"),
                        "changePercent": change_percent,
                        "tradingDate": item.get("tradingDate"),
                    }
                )

        sorted_data = sorted(
            filtered_data, key=lambda x: x["changePercent"], reverse=True
        )

        return {"source": "Top Sectors", "interval": interval, "data": sorted_data}

    except Exception as e:
        return {"error": str(e)}


@app.get("/top_netforeign")
def get_top_netforeign():
    """
    Fetch top net foreign buy/sell data.
    """
    from trade_summary.top_netforeign import fetch_top_netforeign

    try:
        netforeign_data = fetch_top_netforeign()

        top_buy_raw = netforeign_data.get(
            "NETFOREIGN_HSX_HNX_UPCOM_VOL_1D_BUY", {}
        ).get("data", [])

        top_sell_raw = netforeign_data.get(
            "NETFOREIGN_HSX_HNX_UPCOM_VOL_1D_SALE", {}
        ).get("data", [])

        top_buy = [
            {"ticker": item["text"], "value": item["value"]} for item in top_buy_raw
        ]
        top_sell = [
            {"ticker": item["text"], "value": item["value"]} for item in top_sell_raw
        ]

        return {"source": "Top Net Foreign", "top_buy": top_buy, "top_sell": top_sell}

    except Exception as e:
        return {"error": str(e)}


@app.get("/top_interested_stocks")
def get_top_interested_stocks():
    """
    Fetch top interested stocks data.
    """
    from trade_summary.top_interested_stocks import fetch_top_interested_stocks

    try:
        top_stocks = fetch_top_interested_stocks()
        return {"source": "Top Interested Stocks", "data": top_stocks}
    except Exception as e:
        return {"error": str(e)}


@app.get("/khoi_tu_doanh")
def get_khoi_tu_doanh(period: str = Query("1W", regex="^(1W|1M|6M|1Y|YTD)$")):
    """
    Fetch Khoi Tu Doanh data for a given period.
    """
    from trade_summary.khoi_tu_doanh import get_data_khoi_tu_doanh

    try:
        khoi_tu_doanh_data = get_data_khoi_tu_doanh(period)
        return khoi_tu_doanh_data
    except Exception as e:
        return {"error": str(e)}


@app.get("/khoi_ngoai")
def get_khoi_ngoai(period: str = Query("1D", regex="^(1D|1W|1M|3M|6M|1Y)$")):
    """
    Fetch Khoi Ngoai data for a given period.
    """
    from trade_summary.khoi_ngoai import get_data_khoi_ngoai

    try:
        khoi_ngoai_data = get_data_khoi_ngoai(period)
        return khoi_ngoai_data
    except Exception as e:
        return {"error": str(e)}


@app.get("/index_summary")
def get_index_summary():
    """
    Fetch index summary data.
    """
    from trade_summary.index_summary import fetch_index_summary

    try:
        index_summary_data = fetch_index_summary()
        return {"source": "Index Summary", "data": index_summary_data}
    except Exception as e:
        return {"error": str(e)}


@app.get("/index_fluctuation")
def get_index_fluctuation(index_name: str = Query("HSX", enum=["HSX", "HNX", "UPCOM"])):
    """
    Fetch index fluctuation data for a given index name (HSX, HNX, or UPCOM).
    """
    from trade_summary.index_fluctuation import fetch_index_fluctuation

    try:
        index_fluctuation_data = fetch_index_fluctuation(index_name)
        return {
            "source": "Index Fluctuation",
            "index_name": index_name,
            "data": index_fluctuation_data,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/top_news")
def get_top_news(
    date_news=Query(
        default=datetime.now().date(),
        description="Date in YYYY-MM-DD format",
    ),
    type_news=Query(
        default="stock",
        enum=[
            "stock",
            "newest",
            "popular",
            "company",
            "financial",
            "realestate",
            "macroeconomic",
            "worldnews",
            "communitynews",
        ],
    ),
):
    """
    Fetch top news articles from various sources.
    """
    from trade_summary.top_news import fetch_top_news_with_date

    try:
        top_news_data = fetch_top_news_with_date(date_news, type_news)
        return {"source": "Top News", "data": top_news_data}
    except Exception as e:
        return {"error": str(e)}


@app.get("/yahoo_finance_news")
def get_yahoo_finance_news():
    """
    Fetch international news articles from various sources.
    """
    from international_news.yah_news import fetch_yah_news

    try:
        yah_news_data = fetch_yah_news()
        return {"source": "International News", "data": yah_news_data}
    except Exception as e:
        return {"error": str(e)}


@app.get("/market_watch_news")
def get_market_watch_news():
    """
    Fetch stock market news from MarketWatch.
    """
    from international_news.market_watch_news import fetch_market_watch_news

    try:
        market_watch_news_data = fetch_market_watch_news()
        return {"source": "MarketWatch News", "data": market_watch_news_data}
    except Exception as e:
        return {"error": str(e)}
