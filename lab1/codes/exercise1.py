import re
import urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def parseURL(content, url=None):

    urlset = set()
    ########################

    useless_url_list = [r'/', 
                        r'javascript:', 
                        r'javascript:void(0)',
                        r'javascript:;',
                        r'javascript:void(0);',
                        r'#']

    # the list contains useless values of the attribute 'href', we will
    # not add them into our results.


    soup = BeautifulSoup(content, features='html.parser')
    # use BeautifulSoup to parse the HTML file.

    all_tag_a = soup.find_all('a')
    # find all the tag 'a'

    results = []

    for tag_a in all_tag_a:
        href = tag_a.get('href')
        # find the value of the 'href' attribute.
        if href is not None and href not in useless_url_list:
            results.append(href)         

    if url is not None:
        for i in range(len(results)):
            results[i] = urljoin(url, results[i])
    # complete all the url.

    urlset = set(results)
    # remove duplicate urls through set() 

    ########################

    return urlset


def write_outputs(urls, filename):
    file = open(filename, 'w', encoding='utf-8')
    for i in urls:
        file.write(i)
        file.write('\n')
    file.close()


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
    urlSet = parseURL(content, url)
    write_outputs(urlSet, "res1.txt")



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
        urlSet = parseURL(content, url)
        write_outputs(urlSet, f"test/res1_test{index}.txt")

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
