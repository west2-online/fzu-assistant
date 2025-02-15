import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import time
import urllib3

# 忽略 SSL 证书警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_notifications(url, half_link, session):
    headers = {
        "Referer": "https://jxxy.fzu.edu.cn/xsgz/xgdt1.htm",
        "Sec-Ch-Ua": '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133")',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
    }

    try:
        # 发送请求
        response = session.get(url, headers=headers, verify=False)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            # 使用 BeautifulSoup 解析 HTML 内容
            soup = BeautifulSoup(response.text, 'html.parser')
            notifications = []
            # 查找所有通知信息
            for dd in soup.select('div.new_list3.mt10 dl dd'):
                # 获取日期
                date = dd.select_one('span').get_text(strip=True)
                element = dd.select('a')[-1]
                title = element['title']
                link = element['href']
                # 将结果保存到通知列表中
                notifications.append({
                    'date': date,
                    'title': title,
                    'link': half_link + link
                })
            return notifications
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"请求时出现错误：{e}")
        return []

if __name__ == '__main__':
    data_list = []
    half = 'https://math.fzu.edu.cn/'  # 网页前缀
    page = 4

    # 设置重试策略
    retry_strategy = Retry(
        total=3,  # 总共重试3次
        status_forcelist=[500, 502, 503, 504],  # 针对这些状态码进行重试
        backoff_factor=1  # 重试间隔时间的倍数
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    for i in range(0, page):
        if i == 0:
            url = 'https://math.fzu.edu.cn/xsgz/xgdt.htm'
        else:
            url = f'https://math.fzu.edu.cn/xsgz/xgdt/{page - i}.htm'
        data = fetch_notifications(url, half, session)
        data_list += data
        print(i, ':down')
        time.sleep(1)  # 每次请求后等待1秒

    with open("./data/数统学工通知.json", "w", encoding="utf-8") as json_file:
        json.dump(data_list, json_file, ensure_ascii=False, indent=4)
