from datetime import datetime
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://vietnambiz.vn/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
}


def fetch_vnb_news(date_post=""):
    """
    date_post format: 'd-m-yyyy'
    """
    if date_post:
        url = f"https://vietnambiz.vn/chung-khoan/{date_post}.htm"
    else:
        url = "https://vietnambiz.vn/chung-khoan.htm"

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    # list_posts = soup.find_all("div", class_="news-stream")
    posts = soup.find_all("div", class_="item")
    new_data = []
    for post in posts:
        try:
            title = post.find("h3").text.strip()
            link = post.find("a")["href"]
            raw_time = post.find("span", class_="timeago need-get-timeago").get_text(
                strip=True
            )
            clean_time = datetime.strptime(raw_time, "%H:%M | %d/%m/%Y")
            time_post = clean_time.strftime("%Y-%m-%d %H:%M:%S")

            full_link = f"{BASE_URL}{link}" if not link.startswith("http") else link

            print(f"Title: {title}\nLink: {full_link}\nDate: {time_post}\n")
            if full_link:
                detail_resp = requests.get(full_link, headers=headers)
                if detail_resp.status_code == 200:
                    detail_soup = BeautifulSoup(detail_resp.content, "html.parser")
                    html_content = None
                    html_block = detail_soup.find("div", class_="vnbcb-content flex")
                    if html_block:
                        raw_text = html_block.get_text(separator="\n", strip=True)
                        html_content = " ".join(raw_text.split())

            if title and full_link and time_post and html_content:
                new_data.append(
                    {
                        "title": title,
                        "link": full_link,
                        "time": time_post,
                        "html_content": html_content,
                    }
                )
            else:
                print("Missing data in post, skipping...")
        except Exception as e:
            print(f"Error processing post: {e}")
    return new_data


# news = fetch_vnb_news(date_post="")
