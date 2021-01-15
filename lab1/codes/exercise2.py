import re
import urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def write_outputs(urls, filename):
    file = open(filename, 'w', encoding='utf-8')
    for i in urls:
        file.write(i)
        file.write('\n')
    file.close()


def parseIMG(content, url=None):

    urlset = set()
    ########################

    soup = BeautifulSoup(content, features='html.parser')

    # use BeautifulSoup to parse the HTML file.


    imgs = soup.find_all('img')
    # find all the 'img' tag.

    results = []

    for img in imgs:
        src = img.get('src')
        # find the value of the src attributes.
        if src is not None:
            results.append(src)
    
    if url is not None:
        for i in range(len(results)):
            results[i] = urljoin(url, results[i])
    # complete all the url.

    urlset = set(results)
    # remove duplicate urls through set()


    ########################

    return urlset


def main():
    headers = {
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
                       AppleWebKit/537.36 (KHTML, like Gecko) \
                       Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44',
    }
    # add headers to avoid some websites' 403 Forbidden error.

    url = input("please input the url: ")
    req = urllib.request.Request(url=url, headers=headers)
    content = urllib.request.urlopen(req).read()
    urlSet = parseIMG(content, url)
    write_outputs(urlSet, "res2.txt")


def unit_test():
    def work(url: str, index: int):
        headers = {
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
                        AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44',
        }
        # add headers to avoid some websites' 403 Forbidden error.

        req = urllib.request.Request(url=url, headers=headers)
        content = urllib.request.urlopen(req).read()
        urlSet = parseIMG(content, url)
        write_outputs(urlSet, f"test/res2_test{index}.txt")

    test_urls = [r'https://www.bilibili.com',
                 r'https://tieba.baidu.com',
                 r'https://leetcode-cn.com/',
                 r'https://www.youku.com/',
                 r'https://www.huya.com/',
                 r'https://y.qq.com/']

    for index, url in enumerate(test_urls):
        work(url, index)


if __name__ == '__main__':
    # unit_test()
    main()