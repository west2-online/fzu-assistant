import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re

Dat_dict = {
    'name':'先进海洋',
    'list_url': 'https://xjzz.fzu.edu.cn/api/home/news/list?count=10&category_id=26&page=',
    'page' : 25,
    'detail_url' : 'https://xjzz.fzu.edu.cn/api/home/news/detail?id='
}

def bug(dataf):
    data = []
    # print(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "notice", f"{dataf['name']}.json"))
    for i in range(dataf['page']):
        # break
        time.sleep(0.1)
        
        url = dataf['list_url'] + str(i + 1)

        while(True):
            try:
                response = requests.get(url)
                response.raise_for_status()  # 如果请求失败，则抛出异常
                break
            except Exception as e:
                print(e, "正在重试。。。")
                time.sleep(1)
        response.encoding = 'UTF-8'
        # print(url, response.text)
        # while True:
        #     pass

        dat_js = json.loads(response.text)
        dat_ls = dat_js['data']['data']

        for dat in dat_ls:
            id = dat['id']
            title = dat['title']
            date = dat['release_time']
            introduction = dat['content']
            introduction = re.sub(r'<img[^>]*>','', introduction)
            introduction = re.sub(r'<.*?>', '', introduction)
            link = dataf['detail_url'] + str(id)
            data.append({
                'title': title,
                'date': date,
                'link': link,
                'introduction' : introduction
            })

        print(f'page {i + 1} bugged, data count {len(data)}.')


    # 将数据保存为 JSON 文件
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "notice", "学工通知", f"{dataf['name']}学工通知.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"数据已成功保存到 {dataf['name']}学工通知.json")


if __name__ == "__main__":
    bug(Dat_dict)