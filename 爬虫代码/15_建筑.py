import requests
import json
from lxml import etree

base= "https://jzxy.fzu.edu.cn/xsgz/"
urls = [
    "xshd/25.htm" for i in range(25, 0, -1)
]
urls.insert(0, "xshd.htm")

responses = []
for url in urls:
    url = base + url
    response = requests.get(url)
    response.encoding = "utf-8"
    if response.status_code == 200:
        html_content = response.text
        tree = etree.HTML(html_content)
        target_list = tree.xpath('//*[@id="ny"]/div/div[2]/div[2]/ul')
        if target_list:
            list_items = target_list[0].xpath('.//li')

        for item in list_items:
            link = item.xpath('.//a/@href')
            if link:
                link = link[0]
                base_url = url.rsplit('/', 1)[0]
                full_link = base_url + '/' + link.lstrip('/') if not link.startswith('http') else link

            # 提取标题
            title = item.xpath('.//a/text()')
            title = title[0].strip() if title else ''

            # 提取日期
            date = item.xpath('.//span[@class="date"]/text()')
            date = date[0].strip() if date else ''

            print(f"标题: {title}")
            print(f"链接: {full_link}")
            print(f"日期: {date}")
            print("-" * 50)
            responses.append({
                "title": title,
                "link": full_link,
                "date": date
            })
            with open('建筑学工通知.json', 'w', encoding='utf-8') as f:
                json.dump(responses, f, ensure_ascii=False)
            print("数据已成功写入 output.json 文件。")
    else:
        print("未找到指定的列表。")
else:
    print(f"请求失败，状态码: {response.status_code}")

print(responses)