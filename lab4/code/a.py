# SJTU EE208

import os
import re
import string
import sys

# import urllib.error
# import urllib.parse
# import urllib.request

import requests
from urllib.parse import urljoin
import time

from bs4 import BeautifulSoup


def valid_filename(s):
    valid_chars = '-_.() %s%s' % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


class mycount:
    def __init__(self, n=0):
        self.n = n

    def __call__(self, i):
        self.n += i
        return self.n


get_page_count = mycount(0)
crawl_count = mycount(0)


def get_page(page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
        'Cookie': 'uuid_tt_dd=10_9949675910-1600261491577-371068; dc_session_id=10_1600261491577.490733; Hm_up_6bcd52f51e9b3dce32bec4a3997715ac=%7B%22islogin%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22isonline%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22isvip%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%7D; Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac=6525*1*10_9949675910-1600261491577-371068; __gads=ID=ca4796933d209972:T=1600261492:S=ALNI_MbScM9-rzuqwKvRVhABQjkvI2SFjg; c-login-auto-interval=1601095475563; TY_SESSION_ID=943aef78-0594-47b3-8e20-77b1576e878f; c_segment=12; dc_sid=1a99b40cd7fb2b7ab4654c23c87ed1b1; c_first_ref=www.baidu.com; announcement=%257B%2522isLogin%2522%253Afalse%252C%2522announcementUrl%2522%253A%2522https%253A%252F%252Flive.csdn.net%252Froom%252Fyzkskaka%252F5n5O4pRs%253Futm_source%253D1598583200%2522%252C%2522announcementCount%2522%253A0%252C%2522announcementExpire%2522%253A3600000%257D; SESSION=fae7bc16-f4a8-488d-a8eb-6faabdf92f3b; log_Id_click=4; c_utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-2.channel_param; c_ref=https%3A//www.baidu.com/link; c_first_page=https%3A//blog.csdn.net/qq_32506963/article/details/78498157; c_page_id=default; log_Id_pv=75; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1601128198,1601128422,1601129147,1601129163; log_Id_view=126; dc_tos=qh9r71; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1601129198; c-login-auto=10',
    }

    print('正在爬取' + page)

    try:
        content = requests.get(urljoin('https://', page), headers=headers, timeout=2)
        content.encoding = content.apparent_encoding
        return content
    except requests.exceptions.RequestException as e:
        print(e, end=' ')
        print(get_page_count(1))
        return ''


def get_all_links(content, page):  # 返回所有链接
    links = []
    for i in BeautifulSoup(content.text, features='lxml').findAll('a'):
        url_with_get = i.get('href', '')
        url = url_with_get.split('?')[0]
        links.append(url)
    return links


def union_dfs(a, b):  # 将b中不在a中的元素逐项加入a，a为list
    for e in b:
        if e not in a:
            a.append(e)


def add_page_to_folder(page, content, folder1, index_filename1):  # 将网页存到文件夹里，将网址和对应的文件名写入index.txt中
    index_filename = index_filename1  # index.txt中每行是'网址 对应的文件名'
    folder = folder1  # 存放网页的文件夹
    filename = valid_filename(page)  # 将网址变成合法的文件名
    with open(index_filename, 'a', encoding='utf-8') as index:
        index.write(page + '\t' + filename + '\n')
    if not os.path.exists(folder):  # 如果文件夹不存在则新建
        os.mkdir(folder)
    with open(os.path.join(folder, filename), 'w',encoding='utf-8') as f:
        f.write(content)  # 将网页存入文件


def crawl(seed, max_page):
    tocrawl = [seed]
    crawled = []
    count = 0

    while tocrawl:
        print('crawl' + str(crawl_count(1)))
        page = tocrawl.pop()
        if (page).endswith('.apk') or (page).endswith('.pdf') or (page).endswith('.jpg'):
            print('爬取到非法后缀名：'+page)
            continue
        if page not in crawled:
            # print(page)
            content = get_page(page)  # content包含page文本
            if not content:
                continue
            add_page_to_folder(page, content.text, 'htmlw', 'index.txt')
            outlinks = get_all_links(content, page)
            union_dfs(tocrawl, outlinks)
            crawled.append(page)
            count += 1
            ...
        else:
            print('重复网页'+page+'已经在crawled内')
        print('crawled的长度为'+str(len(crawled)))
        if len(crawled) >= max_page:
            break

    # print('crawl =' + str(count))
    return crawled


if __name__ == '__main__':
    start = time.time()
    seed = 'https://baike.baidu.com/'
    # seed = 'https://cdn2.hubspot.net/hubfs/53/%5BConnect%5D%20Marketing%20Resources%20page/Creating%20an%20Integration%20Strategy%20That%20Goes%20Beyond%20the%20HubSpot%20Playbook_Workshop.pdf?__hstc=20629287.572674dc5db5b59170a499c344709d93.1489600428476.1544199168206.1549662406544.1004&__hssc=20629287.1.1549662406544&__hsfp=3532268881'
    max_page = 100

    '''
    seed = sys.argv[1]
    max_page = sys.argv[2]
    '''
    crawled = crawl(seed, max_page)
    stop = time.time()
    print('运行时间' + str(stop - start))
