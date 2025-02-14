import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

def get_09_all_message():
    base_url = "https://sfl.fzu.edu.cn"

    url_09_first="https://sfl.fzu.edu.cn/xsgz/xgdt.htm"

    date_pattern = re.compile(r'^\d{4}\.\d{2}\.\d{2}$')

    r=requests.get(url=url_09_first,headers=headers)
    r.encoding='utf-8'

    soup = BeautifulSoup(r.text, "html.parser")
    items = []

    for li in soup.find_all("li"):
        a_tag = li.find("a")
        date_tag = li.find("span")
        if a_tag and date_tag:
            href = a_tag.get("href")
            title = a_tag.get_text(strip=True)
            date_text = date_tag.get_text(strip=True)
            if date_pattern.match(date_text):
                items.append({
                    "href": urljoin(base_url, href),
                    "title": title,
                    "date": date_text
                })

    print("page 1 ok")

    num_09=192

    while num_09!=0:
        url_09_second=url_09_second='https://sfl.fzu.edu.cn/xsgz/xgdt/'+str(num_09)+'.htm'
        r = requests.get(url=url_09_second, headers=headers)
        r.encoding = 'utf-8'

        soup = BeautifulSoup(r.text, "html.parser")

        for li in soup.find_all("li"):
            a_tag = li.find("a")
            date_tag = li.find("span")
            if a_tag and date_tag:
                href = a_tag.get("href")
                title = a_tag.get_text(strip=True)
                date_text = date_tag.get_text(strip=True)
                if date_pattern.match(date_text):
                    items.append({
                        "href": urljoin(base_url, href),
                        "title": title,
                        "date": date_text
                    })
        print(f"page {192-num_09+2} ok")
        num_09-=1

    df = pd.DataFrame(items)
    df.to_csv('09_message.csv', encoding='utf-8-sig', index=False)
    print("All pages done, CSV saved")
    print("09 url get")

'''
def fetch_description(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and 'content' in meta_tag.attrs:
            print("ok 09")
            return meta_tag['content'].strip()
        else:
            return None
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

'''

if __name__=="__main__":
    print("hello world")

    print("09 start")
    get_09_all_message()
    print()

    '''
    print("09 detailed")
    df09 = pd.read_csv('09_message.csv', encoding='utf-8-sig')
    df09['viewport'] = df09['href'].apply(fetch_description)
    df09.to_csv('09_message_with_desc.csv', encoding='utf-8-sig', index=False)
    print("09 get viewport ok")
    '''

    print("all ok!")