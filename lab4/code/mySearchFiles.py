# SJTU EE208

import sys, os, lucene

from java.io import File
from org.apache.lucene.analysis.cjk import CJKAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version

def valid_file_name(s):
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

def run(searcher, analyzer):
    '''
        Repeatedly get the results correspoing to the 
    '''
    # while True:
    print()
    print ("Hit enter with no input to quit.")
    if not os.path.exists("search_result"):
        os.mkdir("search_result")
    # command = raw_input("Query:")
    # command = unicode(command, 'GBK')

    while True:
        command = input("please input the query: ")
        if not command:
            break
        limit = int(input("please input the maximum retrieval file number: "))
        new_path = 'search_result/{}'.format(valid_file_name(command))
        if not os.path.exists(new_path):
            os.mkdir(new_path)


        print()
        print ("Searching for:", command)
        query = QueryParser("name", analyzer).parse(command)
        # parse the query and get the results.
        scoreDocs = searcher.search(query, int(limit)).scoreDocs
        result_file = open(new_path + "/result_index.txt", "w", encoding='utf-8')
        
        print ("%s total matching documents." % len(scoreDocs))

        for i, scoreDoc in enumerate(scoreDocs):
            # read the title, path, name and url from the results,
            # and print them in the terminal.
            # besides, print the content in result_content\_.txt
            doc = searcher.doc(scoreDoc.doc)
            title, path, name, url = doc.get("title"), doc.get("path"), doc.get("name"), doc.get('url')
            
            read_file = open(path, 'r', encoding='utf-8')
            content = ''.join(read_file.readlines())
            read_file.close()
            
            result_file.write(
                f'id:{i + 1}, \n' +
                f'title: {title}, \n' + 
                f'path: {path}, \n' + 
                f'name: {name}, \n' +
                f'url: {url}, \n' + 
                f'score: {scoreDoc.score} \n') # write to terminal

            print(f'id:{i + 1}, \n' +
                f'title: {title}, \n' + 
                f'path: {path}, \n' + 
                f'name: {name}, \n' +
                f'url: {url}, \n' + 
                f'score: {scoreDoc.score}')   # write to file

            title = valid_file_name(title)
            if len(title) > 20:
                title = title[:20] + '...'
            
            
            content_file = open(new_path + f'/{i + 1}_{title}.html', 'w', encoding='utf-8')
            content_file.write(content)
            content_file.close()

            # print ('path:', doc.get("path"), 'name:', doc.get("name"), 'score:', scoreDoc.score)
                # print 'explain:', searcher.explain(query, scoreDoc.doc)

        result_file.close()


if __name__ == '__main__':

    STORE_DIR = "my_index"
    #initialize.
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print ('lucene', lucene.VERSION)
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = CJKAnalyzer()#Version.LUCENE_CURRENT)
    run(searcher, analyzer)
    del searcher
