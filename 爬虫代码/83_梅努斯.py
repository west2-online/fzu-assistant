import requests
from bs4 import BeautifulSoup
import json
import os
import time

List = {
    "法学院" : {
        "name" : "法学院",
        "url" : "https://law.fzu.edu.cn/xg2/xgdt",
        "page" : 86
    },
    "人文" : {
        "name" : "人文",
        "url" : "https://renwen.fzu.edu.cn/xsgz/xyxw",
        "page" : 104
    },
    "梅努斯" : {
        "name" : "梅努斯",
        "url" : "https://miec.fzu.edu.cn/xssw/xsdt",
        "page" : 28
    }
}
def bug(dataf):
    data = []
    # print(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "notice", f"{dataf['name']}.json"))
    for i in range(dataf['page']):
        # break
        time.sleep(0.1)
        
        if(i == 0):
            url = dataf['url'] + ".htm"
        else:
            url = dataf['url'] + "/" + str(dataf['page'] - i) + ".htm"

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

        # 解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')


        ul_element = soup.find('ul', class_='img-ul-a clearfix')

        if ul_element:
            for li in ul_element.find_all('li'):
                title_element = li.find('a')
                if title_element:
                    title = title_element['title']
                    link = dataf['url'][:-9] + title_element['href']
                    # print(li)
                    # print(li.find('div', class_ = 'img-ul-date'))
                    # print(li.find('div', class_ = 'img-ul-p'))
                    date = li.find('div', class_ = 'img-ul-date').get_text(strip=True)
                    introduction = li.find('div', class_ = 'img-ul-p').get_text(strip=True)
                    # date_element = li.find('div', class_='sj')
                    # date = date_element.find('p', class_='p1').get_text(strip=True) if date_element else 'N/A'
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
    bug(List["梅努斯"])