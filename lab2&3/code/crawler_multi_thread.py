# SJTU EE208

import threading
import queue
import string
import time
import re
import sys
import os
try:   
    from lxml import etree
    from bs4 import BeautifulSoup
except ImportError:
    print('Requirements not satisfied! Please run: pip install -r requirements.txt')
import urllib.request
import urllib.error
import urllib.parse

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
        content = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', 'ignore')
    except BaseException as e:
        print(e)
        return None
    else:
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


def add_page_to_folder(page, content):  # 将网页存到文件夹里，将网址和对应的文件名写入index.txt中
    index_filename = 'index.txt'  # index.txt中每行是'网址 对应的文件名'
    folder = 'html_multi'  # 存放网页的文件夹
    filename = valid_filename(page)  # 将网址变成合法的文件名
    filename = filename + '.html'
    index = open(index_filename, 'a')
    index.write(str(page.encode('ascii', 'ignore')) + '\t' + filename + '\n')
    index.close()
    if not os.path.exists(folder):  # 如果文件夹不存在则新建
        os.mkdir(folder)
    f = open(os.path.join(folder, filename), 'w', encoding='utf-8')
    f.write(str(content))  # 将网页存入文件
    f.close()


def working():
    global count

    while True:
        page = q.get()
        if count >= max_page:
            q.task_done()
            return

        print(f'current page: {page}')
        # pages = get_page(page) # get the content of the page
        content = get_content(page)

        if content is None: # which means that some error occured when trying to get the content of the page.
            q.task_done()
            continue

        add_page_to_folder(page, content) # add the page to the folder we use to store the pages we get.
        outlinks = get_all_links(content, page) # get the links of the page.

        if varLock.acquire():
            for link in outlinks:
                if link not in crawled:
                    q.put(link)
                    crawled.add(link)
                
            print(f'task complete: {count}/{max_page}')
            crawled.add(page)
            count += 1
        varLock.release()
        q.task_done()


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
            print(1)
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
   

    start = time.time()        # start time.
    count = 0                  # the number of pages we have saved in our local machine.
    crawled = set([seed])            # A set used to determine whether a URL is crawled or not.
    varLock = threading.Lock() # the lock used to avoid unpredictable error caused by multithread.
    q = queue.Queue()
    q.put(seed)

    thread_list = []           # the list used to store all the subthreads.

    for i in range(4):
        t = threading.Thread(target=working)
        t.setDaemon(True)      # set the thread to be a deamon thread.
        thread_list.append(t)
        t.start()
    
    for x in thread_list:
        x.join()               # the main thread will wait here until the task was
                               # completed by the subthreads.
    
    end = time.time()
    print(end - start)         # calculate the consumed time.

    with open('crawled.txt', 'w', encoding='utf-8') as f:
        for x in crawled:
            f.write(x)
            f.write('\n')      # print all the crawled URL into the file f.