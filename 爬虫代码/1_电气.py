import requests
from bs4 import BeautifulSoup
import json
import urllib3

# 忽略 SSL 证书警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_notifications(url,half_link):
    headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Referer": "https://dqxy.fzu.edu.cn/xsgz/xgdt/37.htm",
    "Sec-Ch-Ua": '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133")',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
    "Cookie": "_gscu_1331749010=0217857053mowu18; __root_domain_v=.fzu.edu.cn; _qddaz=QD.377439171235310; tfstk=gtLEhAX0Z23ElwYEE1bzui_ihs7dWwDXZU65ZQAlO9XhAHMPzdWwR61WAQYwEdICqyGd4uAJCgx7V6tazKdVqeO5-WK9hI4BRDQ7zwQRrxMjlqGp9aQoRytB_9dM6_c1t8qwV47RrxM_t-uU0apvshYMxCcNN_C3xLj3SlXOaTqkE9jgIs5ArTvkElAGZ_UlZg4lSf5RITblrLAiZVvkpPWNxbmjPrvoxGjFnBXazBLNtMrptOzurF-NYt2PQz4k76Rs7lu_u06DD9sfhd0_8aRGap66nq4NSi-vN_JE8ybBjhLdRFM4MMJPQiY1bmVw3wJPmejaZzOV89_NsEc7DOTNdLYFjjaVVNYfmwxsXvs58sJkJpPzrKA6GeI9zxyGeH1ASsOK8P7Dt_jy98CiT8TJY8qPx1CNhflNj5eepBo4y6Z82GoO_tGxMuERx1CNhfla2uIwW1WjMjC..; JSESSIONID=02889884744A5D955D6F80D9EECEEE28"
}
    try:
        # 发送请求
        response = requests.get(url, headers=headers, verify=False)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            # 使用 BeautifulSoup 解析 HTML 内容
            soup = BeautifulSoup(response.text, 'html.parser')
            notifications = []
            # 查找所有通知信息
            for li in soup.select('div.r-content ul li'):
                # 获取日期
                date = li.select_one('span.date').get_text(strip=True)
                element = li.select_one('a')
                title = element['title']
                link = element['href']
                # 将结果保存到通知列表中
                notifications.append({
                    'date': date,
                    'title': title,
                    'link': half_link+link
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
    half = 'https://dqxy.fzu.edu.cn/'  # 网页前缀
    page = 38
    for i in range(0,page):
        if i == 0:
            url ='https://dqxy.fzu.edu.cn/xsgz/xgdt.htm'
        else:
            url = f'https://dqxy.fzu.edu.cn/xsgz/xgdt/{page-i}.htm'
        data = fetch_notifications(url, half)
        data_list += data
        print(i,':down')
        # print(data)

    with open("./data/电气学工通知.json", "w", encoding="utf-8") as json_file:
        json.dump(data_list, json_file, ensure_ascii=False, indent=4)