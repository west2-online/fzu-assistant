import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

def get_13_all_message():
    base_url = "https://chem.fzu.edu.cn"

    url_13_first="https://chem.fzu.edu.cn/xsgz/xwdt.htm"

    date_pattern = re.compile(r'^\d{4}\.\d{2}\.\d{2}$')

    r=requests.get(url=url_13_first,headers=headers)
    r.encoding='utf-8'

    soup = BeautifulSoup(r.text, "html.parser")
    items = []

    for a_tag in soup.select("div.news-list a.news-item"):
        raw_href = a_tag.get("href", "").strip()
        full_url = urljoin(base_url, raw_href)

        day = a_tag.select_one("div.news-date .news-day")
        month = a_tag.select_one("div.news-date .news-month")

        if day and month:
            date_str = f"{month.get_text(strip=True)}-{day.get_text(strip=True)}"
        else:
            date_str = ""

        title_div = a_tag.select_one("div.news-content .news-title")
        title_text = title_div.get_text(strip=True) if title_div else ""

        desc_div = a_tag.select_one("div.news-content .news-desc")
        desc_text = desc_div.get_text(strip=True) if desc_div else ""

        items.append({
            "href": full_url,
            "title": title_text,
            "date": date_str,
            "summary": desc_text
        })

    for item in items:
        print(item)

    print("page 1 ok")

    num_13=83

    while num_13!=0:
        url_13_second='https://chem.fzu.edu.cn/xsgz/xwdt/'+str(num_13)+'.htm'
        r = requests.get(url=url_13_second, headers=headers)
        r.encoding = 'utf-8'

        soup = BeautifulSoup(r.text, "html.parser")

        for a_tag in soup.select("div.news-list a.news-item"):
            raw_href = a_tag.get("href", "").strip()
            full_url = urljoin(base_url, raw_href)

            day = a_tag.select_one("div.news-date .news-day")
            month = a_tag.select_one("div.news-date .news-month")

            if day and month:
                date_str = f"{month.get_text(strip=True)}-{day.get_text(strip=True)}"
            else:
                date_str = ""

            title_div = a_tag.select_one("div.news-content .news-title")
            title_text = title_div.get_text(strip=True) if title_div else ""

            desc_div = a_tag.select_one("div.news-content .news-desc")
            desc_text = desc_div.get_text(strip=True) if desc_div else ""

            items.append({
                "href": full_url,
                "title": title_text,
                "date": date_str,
                "summary": desc_text
            })


        print(f"page {83-num_13+2} ok")
        num_13-=1

    df = pd.DataFrame(items)
    df.to_csv('13_message.csv', encoding='utf-8-sig', index=False)
    print("All pages done, CSV saved")
    print("13 url get")

if __name__=="__main__":
    print("hello world")

    print("13 start")
    get_13_all_message()
    print()

    print("all ok!")