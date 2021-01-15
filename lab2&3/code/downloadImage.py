import requests
import matplotlib.pyplot as plt
import os
import sqlite3

def mkdir(s):
    if not os.path.exists(s):
        os.mkdir(s)

def download_image():
    while not Q.empty():
        task = Q.get()
        print(task[1][-2])
        imgLinks = eval(task[1][-2])
        if not imgLinks:
            Q.task_done()
            continue
        else:
            link = 'https:' + imgLinks[0]
        success = False
        for n_trait in range(5):
            # 至多尝试5次重复下载
            try:
                re = requests.get(link)
            except BaseException as e:
                print(f'{task[0]}: exception: {e}: n_trait={n_trait}')
                n_trait += 1
            else:
                success = True
                break
        if not success:
            Q.task_done()
            continue
        else:
            file_path = f'imgs/{task[1][-1]}/{task[0]}.jpg'
            mkdir(file_path)
            content = re.content
            with open(file_path, 'wb') as fw:
                fw.write(content)
            Q.task_done()

db = sqlite3.connect('data/MSN_ALL.db')
allData = db.execute('SELECT * FROM MSN')
allData = list(allData)

mkdir('imgs')
mkdir('imgs/politics')
mkdir('imgs/technology')

# 修改此处以改变起始/结束的地方

start = 0
end = 100

import threading
import queue

N_THREADS = 8
thread_pool = []
Q = queue.Queue()

for i, x in enumerate(allData[start : end]):
    Q.put((i + start, x))

for i in range(N_THREADS):
    t = threading.Thread(target=download_image)
    t.setDaemon(True)
    thread_pool.append(t)
    t.start()

Q.join()