# SJTU EE208

import re
import sys
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup


def parseZhihuDaily(content, url):
    zhihulist = list()
    ########################


    # The parts of the HTML file containing what we need is like this:
    # <div class='box'>
    #     <a href=URL>
    #         <img src=IMG> </img>
    #         <span> TITLE </span>
    #     </a>
    # </div>
    
    soup = BeautifulSoup(content, features='html.parser')
    # parse the content through BeautifulSoup

    boxes = soup.find_all('div', {'class': 'box'})
    # find all the 'div' tags whose class attributes are 'box'

    for element in boxes:
        tag_a = element.a
        href = 'https://daily.zhihu.com' + tag_a['href']
        img = tag_a.contents[0]['src']
        title = tag_a.contents[1].text
        zhihulist.append([img, title, href])

    ########################

    return zhihulist


def write_outputs(zhihus, filename):
    file = open(filename, "w", encoding='utf-8')
    for zhihu in zhihus:
        for element in zhihu:
            file.write(element)
            file.write('\t')
        file.write('\n')
    file.close()


def main():
    headers = {
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
		               AppleWebKit/537.36 (KHTML, like Gecko) \
		               Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44',
	}
    # add headers to avoid some websites' 403 Forbidden error.

    url = r'https://daily.zhihu.com/'
    req = urllib.request.Request(url=url, headers=headers)
    content = urllib.request.urlopen(req).read()
    zhihus = parseZhihuDaily(content, url)
    write_outputs(zhihus, "res3.txt")


if __name__ == '__main__':
    main()
