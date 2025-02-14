import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

def get_10_all_message():
    base_url = "https://ccds.fzu.edu.cn/"

    url_10_first="https://ccds.fzu.edu.cn/xsgz/dtxw.htm"

    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')

    r=requests.get(url=url_10_first,headers=headers)
    r.encoding='utf-8'

    soup = BeautifulSoup(r.text, "html.parser")
    items = []

    for dd in soup.find_all("dd", id=re.compile(r"^line_u9_")):
        a_tag = dd.find("a")
        date_tag = dd.find("span", class_="fr gray")
        if a_tag and date_tag:
            href = a_tag.get("href")
            title = a_tag.get_text(strip=True)
            date_text = date_tag.get_text(strip=True)
            if date_pattern.match(date_text):
                full_url = urljoin(base_url, href)
                items.append({
                    "href": full_url,
                    "title": title,
                    "date": date_text
                })

    print("page 1 ok")

    num_10=37

    while num_10!=0:
        url_09_second=url_09_second='https://ccds.fzu.edu.cn/xsgz/dtxw/'+str(num_10)+'.htm'
        r = requests.get(url=url_09_second, headers=headers)
        r.encoding = 'utf-8'

        soup = BeautifulSoup(r.text, "html.parser")

        for dd in soup.find_all("dd", id=re.compile(r"^line_u9_")):
            a_tag = dd.find("a")
            date_tag = dd.find("span", class_="fr gray")
            if a_tag and date_tag:
                href = a_tag.get("href")
                title = a_tag.get_text(strip=True)
                date_text = date_tag.get_text(strip=True)
                if date_pattern.match(date_text):
                    full_url = urljoin(base_url, href)
                    items.append({
                        "href": full_url,
                        "title": title,
                        "date": date_text
                    })
        print(f"page {37-num_10+2} ok")
        num_10-=1

    df = pd.DataFrame(items)
    df.to_csv('10_message.csv', encoding='utf-8-sig', index=False)
    print("All pages done, CSV saved")
    print("10 url get")

if __name__=="__main__":
    print("hello world")

    print("10 start")
    get_10_all_message()
    print()

    print("all ok!")
