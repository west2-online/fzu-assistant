import requests
from lxml import etree
import time

List=[]
Title=[]
Date=[]

# 目标URL
url = "https://jgxy.fzu.edu.cn/xsgz/xgdt.htm"

# 设置请求头，加入User-Agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
}

# 发送HTTP请求获取网页内容
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'  # 设置编码为utf-8

# 解析HTML内容
html = etree.HTML(response.text)

titles = html.xpath('//div[@class="list_news"]//a/@title')
links = html.xpath('//div[@class="list_news"]//a/@href')
dates = html.xpath('//div[@class="list_news"]//a/span/text()')
print(dates)
time.sleep(1)
Title = Title + titles
Date = Date + dates
time.sleep(1)
L=[]
for title in titles:
    print(title.strip())
for link in links:
    Link = url.split("/")[0] + '//' + url.split("/")[2] + '/' + link.split("/")[1] + '/' + link.split("/")[
        2] + '/' + link.split("/")[3]
    L.append(Link)
    print(Link)
List = List + L
for date in dates:
    print(date.strip())
#
# 目标URL
base = "https://jgxy.fzu.edu.cn/xsgz/xgdt"
numbers=[
    f"/{i}.htm" for i in range(117, 0, -1)
]
for u in numbers:
    url=base+u

    while (True):
        try:
            # 发送HTTP请求获取网页内容
            response = requests.get(url, headers=headers)
            response.encoding = 'utf-8'  # 设置编码为utf-8
            break
        except Exception as e:
            print(e, "正在重试")

    # 解析HTML内容
    html = etree.HTML(response.text)

    # 使用XPath提取学工新闻板块的每个文章标题
    titles = html.xpath('//div[@class="list_news"]//a/@title')
    links = html.xpath('//div[@class="list_news"]//a/@href')
    dates = html.xpath('//div[@class="list_news"]//a/span/text()')
    print(dates)

    Title = Title + titles
    Date = Date + dates
    time.sleep(1)
    L=[]
    for title in titles:
        print(title.strip())
    for link in links:
        Link = url.split("/")[0] + '//' + url.split("/")[2] + '/' + link.split("/")[2] + '/' + link.split("/")[
            3] + '/' + link.split("/")[4]
        L.append(Link)
        print(Link)
    List = List + L
    for date in dates:
        print(date.strip())


print("##################################")
for line in List:
    print(line)
print("##################################")
for line in Title:
    print(line)
print("##################################")
for line in Date:
    print(line)

