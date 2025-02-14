import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

def get_11_all_message():
    base_url = "https://wx.fzu.edu.cn/"

    url_11_first = "https://wx.fzu.edu.cn/xgdt/xgxw.htm"

    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')

    r = requests.get(url_11_first, headers=headers)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, "html.parser")

    items = []
    for li in soup.find_all("li"):
        a_tag = li.find("a")
        date_span = li.find("span")
        summary_p = li.find("p")
        if a_tag and date_span and summary_p:
            raw_href = a_tag.get("href", "")
            title = a_tag.get("title", "").strip()
            date_text = date_span.get_text(strip=True)
            summary = summary_p.get_text(strip=True)
            if date_pattern.match(date_text):
                full_url = urljoin(base_url, raw_href)
                items.append({
                    "href": full_url,
                    "title": title,
                    "date": date_text,
                    "summary": summary
                })

    for item in items:
        print(item)

    print("page 1 ok")

    num_11=37

    while num_11!=0:
        url_11_second=url_09_second='https://wx.fzu.edu.cn/xgdt/xgxw/'+str(num_11)+'.htm'
        r = requests.get(url=url_09_second, headers=headers)
        r.encoding = 'utf-8'

        soup = BeautifulSoup(r.text, "html.parser")

        for li in soup.find_all("li"):
            a_tag = li.find("a")
            date_span = li.find("span")
            summary_p = li.find("p")
            if a_tag and date_span and summary_p:
                raw_href = a_tag.get("href", "")
                title = a_tag.get("title", "").strip()
                date_text = date_span.get_text(strip=True)
                summary = summary_p.get_text(strip=True)
                if date_pattern.match(date_text):
                    full_url = urljoin(base_url, raw_href)
                    items.append({
                        "href": full_url,
                        "title": title,
                        "date": date_text,
                        "summary": summary
                    })
        print(f"page {37-num_11+2} ok")
        num_11-=1

    df = pd.DataFrame(items)
    df.to_csv('11_message.csv', encoding='utf-8-sig', index=False)
    print("All pages done, CSV saved")
    print("10 url get")


if __name__ == "__main__":
    print("hello world")

    print("11 start")
    get_11_all_message()
    print()

    print("all ok!")