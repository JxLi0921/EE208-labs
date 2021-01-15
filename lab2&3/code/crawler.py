# SJTU EE208

import os
import re
import string
import sys
import urllib.error
import urllib.parse
import time
try:    
    from lxml import etree
except ImportError:
    print(print('Requirements not satisfied! Please run: pip install -r requirements.txt'))
import urllib.request

from bs4 import BeautifulSoup


def valid_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    if len(s) > 127:
        s = s[:127] # avoid file name too long error.
    return s


def get_content(page):
    '''
        get the content of a page.
        Input:
            page: str.
        Return:
            content: str.
    '''

    headers = {
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
		               AppleWebKit/537.36 (KHTML, like Gecko) \
		               Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44',
	}
    # add headers to avoid some websites' 403 Forbidden error.

    try:
        req = urllib.request.Request(url=page, headers=headers)
        content = urllib.request.urlopen(req, timeout=2).read().decode('utf-8')
    except BaseException:
        print('error!')
        return None
    return content

def get_all_links(content, page, method='lxml'):
    '''
        get all the links of the page.

        Input:
            content: the content of the given page.
            page: the URL of the page.
            method: it should be 'lxml' or 'BeautifulSoup', 
                    determining which method to be used to process the content. 
                    By default we will use 'lxml', for the reason that it is
                    much faster.
        Return:
            links: list, containing all the useful 'href's of the given page's content. 
    '''
    
    def valid_str(s: str):
        '''
            Check whether the string s is a valid URL.

            A valid URL should be a absolute address
            or a relative address beginning with '//'.
        '''
        return (len(s) > 1 and s[:2] == '//') \
               or (len(s) > 3 and s[:4] == 'http')

    links = None
    target_pattern = re.compile('^http|^/')

    if method == 'lxml':
        # get all the links through 'lxml' and its xpath method.
        links = etree.HTML(content.encode('utf-8')).xpath('//a/@href')
        links = [urllib.parse.urljoin(page, x) for x in links if valid_str(x)]
    elif method == 'BeautifulSoup':
        # get all the links through 'BeautifulSoup'
        soup = BeautifulSoup(content, features="html.parser")
        tag_a = soup.find_all('a', {'href': re.compile('^http|^/')})
        links = [x['href'] for x in tag_a]
        links = [urllib.parse.urljoin(page, x) for x in links]
    else:
        raise ValueError

    return list(set(links)) # remove duplicate


def valid_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    if len(s) > 127:
        s = s[:127] # avoid file name too long error.
    return s


def union_dfs(c, a, b):
    for e in b:
        if e not in a and e not in c:
            a.append(e)
            c.add(e)


def add_page_to_folder(page, content):  # 将网页存到文件夹里，将网址和对应的文件名写入index.txt中
    index_filename = 'index.txt'  # index.txt中每行是'网址 对应的文件名'
    folder = 'html'  # 存放网页的文件夹
    filename = valid_filename(page)  # 将网址变成合法的文件名
    index = open(index_filename, 'a')
    index.write(str(page.encode('ascii', 'ignore')) + '\t' + filename + '\n')
    index.close()
    if not os.path.exists(folder):  # 如果文件夹不存在则新建
        os.mkdir(folder)
    f = open(os.path.join(folder, filename), 'w', encoding='utf-8')
    f.write(str(content))  # 将网页存入文件
    f.close()


def crawl(seed, max_page):
    tocrawl = [seed]
    crawled = set([seed])
    count = 0

    while tocrawl:
        page = tocrawl.pop()
        print(f'第{count + 1}/{max_page}个网页: {page}') 
        content = get_content(page) # get the content of the page
        if content is None: # which means that some error occured when trying to get the content of the page.
            continue
        add_page_to_folder(page, content) # add the page to the folder we use to store the pages we get.
        outlinks = get_all_links(content, page) # get the links of the page.
        union_dfs(crawled, tocrawl, outlinks) # add all the links in the page which is not crawled into the list 'tocrawl'
        crawled.add(page) # mark the page to avoid duplication.
        count += 1
        if count >= max_page:
            break
    return crawled


def get_seed_and_maxPage():
    '''
        get the seed and max page number from 
        whether command line argument or console input.
    '''

    seed = None
    max_page = None

    if len(sys.argv) == 1:
        seed = input("please input the seed URL: ")
        while True:
            try:
                max_page = int(input("please input the max page number: "))
            except ValueError:
                print("Invalid max page number, please input again: ")
            else:
                break
    else:
        _, seed, max_page = sys.argv
        while True:
            try:
                max_page = int(max_page)
            except ValueError:
                max_page = input("Invalid max page number, please input again: ")
            else:
                break

    return seed, max_page


if __name__ == '__main__':
    print('current folder: ', os.getcwd())
    seed, max_page = get_seed_and_maxPage()
    start = time.time()
    crawled = crawl(seed, max_page)
    print(time.time() - start)