# SJTU EE208

import sys, os, lucene
from hightlighter import Highlighter

from java.io import File
from java.io import StringReader
from org.apache.lucene.analysis import TokenStream
from org.apache.lucene.analysis.cjk import CJKAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher, BooleanQuery
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanClause


class Searcher:
    def __init__(self, store_dir: str) -> None:
        self.max_length = 30
        self.store_dir = store_dir
        self.vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    
    def __cut_contents(self, keys: list, value: str) -> str:
        '''
            Cut the str(value) to make it suitable for display on the website.
            otherwise it will be too long.

            Algorithm: if the str(value) contains keys, we cut the str from 
                       max(0, first_key_found_position - super_factor) to 
                       min(first_key_found_position + super_factor, len(str))

                       super_factor is a constant 70.

            Input: 
                keys: list.
                value: str.
            Return:
                the cutted contents -> str.
        '''
        position = len(value) / 2

        # find the first_key_found_position above.
        for key in keys:
            c_position = value.find(key)
            if c_position == -1:
                continue
            position = min(position, c_position)

        # define a super_factor, just to escape 'magic number'.
        super_factor = 70

        if position >= super_factor and position + super_factor < len(value):
            return '......' + value[position-super_factor: position+super_factor] + '......'

        if position + super_factor < len(value):
            return value[0: position + super_factor] + '......'

        if position >= super_factor:
            return '......' + value[position-super_factor: len(value)]
        
        return value
        
        

    def query(self, command_dict: dict) -> list:
        '''
            return a list of highlighted found results of the given query dict.
            Input: command_dict: dict.
            Return: res: list.
        '''

        # initialize
        self.vm_env.attachCurrentThread()
        directory = SimpleFSDirectory(File(self.store_dir).toPath())
        searcher = IndexSearcher(DirectoryReader.open(directory))
        analyzer = CJKAnalyzer()
        querys = BooleanQuery.Builder()
        highlighter = Highlighter([])

        # build the query, and add keywords to the highlighter.
        for key, value in command_dict.items():
            if value:
                query = QueryParser(key, analyzer).parse(value)
                querys.add(query, BooleanClause.Occur.MUST)
                highlighter.add_key(value)

        # search the query in our index.
        scoreDocs = searcher.search(querys.build(), 1000).scoreDocs

        results = []
        
        # all the fields of the index.
        all_keys = set(["title", "url", "author", 'id', 'source', 'photography', 'imgaddr', 'contents'])

        # No results.
        if scoreDocs is None:
            return results

        
        for i, score_doc in enumerate(scoreDocs):
            doc = searcher.doc(score_doc.doc)
            result = {}
            result.setdefault(None)

            # highlight all the value, and cut the contents.
            for key in all_keys:
                value = doc.get(key)
                if key == 'contents':
                    value = self.__cut_contents(highlighter.get_keys(), value)
                result[key] = highlighter.highlight(value)

            results.append(result)

        return results



if __name__ == '__main__':
    pass