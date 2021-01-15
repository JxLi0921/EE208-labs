import threading
import requests
import queue
import os
import re
import sys
import collections
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_text(link: str) -> str:
	'''
		return the text of a given url.
	'''

	response = requests.get(link, timeout=10)
	response.encoding = response.apparent_encoding
	return response.text


def valid_file_name(s: str) -> str:
    '''
        convert s into a valid file name.
        input:
            s: str.
        output:
            s`: str, a valid file name.
    '''
    invalid_chars = r'/\*?:"<>|'
    new_s = ''
    for x in s:
        if x not in invalid_chars:
            new_s = f'{new_s}{x}'
    return new_s


def remove_newline(content: str) -> str:
	'''
		remove continuous duplicate '\n' in a str.
		input:
			original str.
		output:
			new str.
	'''
	new_content = []
	pre_newline = 0

	for x in content:
		if x != '\n':
			new_content.append(x)
			pre_newline = 0
		elif pre_newline < 2:
			new_content.append(x)
			pre_newline += 1

	return ''.join(new_content)


def retrive_information_from_url(href: str) -> tuple:
	'''
		get the information we need from the url href.
		return a tuple containing the information we need.
	'''

	passage_text = get_text(href)
	soup_passage = BeautifulSoup(passage_text, features='lxml')

	# locate the position of the title.
	div_article_title = soup_passage.find('div', {'class': 'Article-title'})
	title = div_article_title.h2.text

	# locate the position which is near the passage.
	div_article_content = soup_passage.find('div', {'class': 'Article_content'})

	content = ''
	author = None
	photography = None
	source = None

	for p in div_article_content.contents:
		# The passage was formed by a series of p tag.
		# Add all these series together, and them we will get the passage we need.
		if p.name == 'p':
			content += p.text + '\n'
		elif p != '\n':
			res = collections.defaultdict(None)
			try:
				# locate author, photography and source.
				if p['class'][0] == 'Article-source':
					for x in p.div.contents:
						
						if x.name == 'div':
							if x.label.text.find('作者') != -1:
								res['作者'] = x.div.text
							elif x.label.text.find('摄影') != -1:
								res['摄影'] = x.div.text
							elif x.label.text.find('供稿单位') != -1:
								res['供稿单位'] = x.div.text

				author, photography, source = res.get('作者'), res.get('摄影'), res.get('供稿单位')
			except:
				pass

	# remove the unnecessary \n from content
	content = remove_newline(content)
	return title, content, author, photography, source


def working():
	global cnt
	while not q.empty():
		url = q.get()
		text = get_text(url)
		base = 'https://news.sjtu.edu.cn'
		soup = BeautifulSoup(text, features='lxml')

		for div_ImgCrop in soup.find_all('div', {'class': 'ImgCrop'}):
			# div_ImgCrop: a div tag with class=ImgCrop,
			# which is pretty close to the href and img_address
			img_address = base + div_ImgCrop.contents[1]['src']
			href = base + div_ImgCrop.parent.parent['href']

			# retrive information from the subpage.
			title, content, author, photography, source = retrive_information_from_url(href)

			# connect the numbers in the string with '_'.
			# example: https://news.sjtu.edu.cn/jdyw/20201015/132343.html -> 20201015_132343
			name = '_'.join(re.findall(r'\d+', href))

			# get the picture from img_address
			f = open(f'pics/{name}.jpg', 'wb')
			try:
				pic = requests.get(img_address, timeout=10)
			except requests.exceptions.ConnectionError:
				print('unable to download the image!')
			else:
				f.write(pic.content)
			f.close()
			
			# write the passage into a txt file.
			f = open(f'passages/{name}.txt', 'w', encoding='utf-8')
			f.write(content)
			f.close()

			if var_lock.acquire():
				# add the information to the index array.
				index.append((name, title, author, photography, source, img_address, href))
				var_lock.release()

		if var_lock.acquire():
			cnt += 1
			print(f'{cnt}')
			var_lock.release()
		q.task_done()


def replace(s: str) -> str:
	'''
		replace a string's ' ' with ','.
	'''
	if s is None:
		return None
	return s.replace(' ', ',')
		

		
num_thread = 8
base = 'https://news.sjtu.edu.cn/jdyw/index{}.html'

q = queue.Queue()
q.put(base.format(''))

for i in range(2, 201):
	q.put(base.format(f'_{i}'))
# put all the url like: https://news.sjtu.edu.cn/jdyw/index*.html into the queue.

var_lock = threading.Lock()
index = [] 

cnt = 0
pool = [] # thread pool

# use multi thread to accelerate the process.
for i in range(num_thread):
	t = threading.Thread(target=working)
	t.setDaemon(True)
	pool.append(t)
	t.start()

for i in range(num_thread):
	t.join()

with open('index_pic.txt', 'w', encoding='utf-8') as f:
	for idx in index:
		name, title, author, photography, source, img_address, href  = idx
		# why replace here:
		# when we need to parse the index_pic.txt, we split each line by ' ',
		# thus we need to replace the ' ' with ',' to avoid potential errors. 
		f.write(f'{replace(name)} {replace(title)} {replace(author)} ' + \
		        f'{replace(photography)} {replace(source)} {img_address} {href}\n')