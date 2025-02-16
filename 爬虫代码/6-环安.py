import requests
from lxml import etree
import time

# 目标URL
url = "https://es.fzu.edu.cn/xsgz/txdt/3.htm"

# 设置请求头，加入User-Agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
}

# 发送HTTP请求获取网页内容
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'  # 设置编码为utf-8

# 解析HTML内容
html = etree.HTML(response.text)

R=[]
# 使用XPath提取学工新闻板块的每个文章标题
titles = html.xpath('//div[@class="ny-right fr"]//div[@class="list"]/ul/li//a/@title')
links = html.xpath('//div[@class="ny-right fr"]//div[@class="list"]/ul/li//a/@href')
dates = html.xpath('//div[@class="ny-right fr"]//div[@class="list"]/ul//span/text()')
# print(dates)
time.sleep(1)
L=[]
# 打印提取的标题
for title in titles:
    print(title.strip())
for link in links:
    Link=url.split("/")[0]+'//'+url.split("/")[2]+'/'+link.split("/")[1]+'/'+link.split("/")[2]+'/'+link.split("/")[3]
    L.append(Link)
    print(Link)
for date in dates:
    print(date.strip())

# # 目标URL
url = "https://civil.fzu.edu.cn/xsgz/"

urls = [
    f"{i}.htm" for i in range(3, 0, -1)
]
for u in urls:
    Url=url+u

    # 目标URL
    url = "https://es.fzu.edu.cn/xsgz/txdt/1.htm"

    # 设置请求头，加入User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
    }

    # 发送HTTP请求获取网页内容
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'  # 设置编码为utf-8

    # 解析HTML内容
    html = etree.HTML(response.text)

    R = []
    # 使用XPath提取学工新闻板块的每个文章标题
    titles = html.xpath('//div[@class="ny-right fr"]//div[@class="list"]/ul/li//a/@title')
    links = html.xpath('//div[@class="ny-right fr"]//div[@class="list"]/ul/li//a/@href')
    dates = html.xpath('//div[@class="ny-right fr"]//div[@class="list"]/ul//span/text()')
    # print(dates)
    time.sleep(1)
    L = []
    # 打印提取的标题
    for title in titles:
        print(title.strip())
    for link in links:
        Link = url.split("/")[0] + '//' + url.split("/")[2] + '/' + link.split("/")[2] + '/' + link.split("/")[
            3] + '/' + link.split("/")[4]
        L.append(Link)
        print(Link)
    for date in dates:
        print(date.strip())