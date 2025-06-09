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
