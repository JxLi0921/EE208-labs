'''
    Creator: Li Jingxiang
    Description:
        A multi thread HTML Cleaner.
        Used to extract the text of the title attribute of the html file,
        and also remove the marks of the html files.
'''


from bs4 import BeautifulSoup
import os
import re
import threading
import queue
import sys


def cleaned(w):
    s = ''
    pre_newline = False
    for x in w:
        if x == '\n':
            if pre_newline:
                continue
            else:
                pre_newline = True
        else:
            pre_newline = False
        s = '{}{}'.format(s, x)
    return s


def working():
    global cnt, orig_path, new_path

    while True:
        if q.empty():
            return

        file_name = q.get() # get the file name from the queue.

        if var_lock.acquire(): 
            print(f'current: {cnt}')
            cnt += 1
            file_path = orig_path + '/' + file_name
            out_path = new_path + '/' + file_name.replace('.html', '.txt')
            var_lock.release()

        if os.path.isfile(file_path):
            f_in = open(file_path, 'r', encoding='utf-8')
            f_out = open(out_path, 'w', encoding='utf-8')

            print('outpath: {}'.format(out_path))

            try:  
                # use try...except to avoid unpredictable errors.
                content = f_in.read()
                soup = BeautifulSoup(content, features='html.parser')
                cleaned_content = cleaned(''.join(soup.get_text()))
                url = filename_to_url[file_name]
                title = soup.title.text
            except:
                f_in.close()
                f_out.close()
                q.task_done()
                continue

            print(f'filename: {file_name}',
                  f'url: {url}',
                  f'title: {title}', sep='\n')

            cleaned_index_file.write(f'{file_name} {url} {title} \n')
            # add the filename, original url and title corresponding to the new html file to the new index file.

            f_out.write(cleaned_content)

            f_out.close()
            f_in.close()
            q.task_done()


orig_path = 'htmls'        # original path name, original HTML stored here.
new_path = 'cleaned_htmls' # new path name, cleaned HTML files will be stored here.

if not os.path.exists(new_path): # create the folder if it's not exist.
    os.mkdir(new_path)

file_names = os.listdir(orig_path) # all the folders and files in the original path. 
cleaned_index_file = open('cleaned_file_index.txt', 'w', encoding='utf-8') # an index file of the cleaned html files.
orig_index_file = open('index.txt', 'r', encoding='utf-8') # index file of original html files.

filename_to_url = {} # create a filename to url mapping through the data from the index of the original html files.
for line in orig_index_file.readlines(): 
    x, y = tuple(line.split())
    filename_to_url[y] = x

orig_index_file.close()

cnt = 0
var_lock = threading.Lock() 
q = queue.Queue()  # create a queue and put the tasks inside, worker can fetch tasks from the queue. 
for file_name in file_names:
    q.put(file_name) # put all file name into the queue.


# create 4 subthreads to clean the HTML files.
for i in range(4):
    t = threading.Thread(target=working)
    t.setDaemon(True)      # set the thread to be a deamon thread.
    t.start()

q.join()