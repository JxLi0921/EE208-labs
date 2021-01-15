# SJTU EE208

import sys, os, lucene
from hightlighter import Highlighter
from cache import Cache

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
import copy
import json

class Searcher:
    def __init__(self, store_dir: str) -> None:
        self.max_length = 30
        self.store_dir = store_dir
        self.vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        self.cache = Cache()

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
        position = len(value) // 2

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
    
    def __parse_command(self, command: dict, H_checked: bool) -> dict:
        def add_to(s1, s2):
            return f"{s1}{'' if s1 == '' else ' '}{s2}"

        allow_opt = set(['title', 'author', 'source', 'photography', 'contents'])
        command_dict = {}
        s = None

        # 由于command 大概为： {'contents': theInputString, 'p_checked': 'on', 'H_checked': 'on}
        # 因此需要把contents从其中先提取出来。

        if H_checked:
            # 进行高级检索，要对输入的字符串进行处理
            try:
                s = command['contents']
            except:
                return {}
            # 对字符串进行解析，对应高级检索
            for i in s.split(' '):
                if ':' in i:
                    opt, value = i.split(':')[:2]
                    
                    opt = opt.lower()
                    if opt in allow_opt and value != '':
                        command_dict[opt] = add_to(command_dict.get(opt, ''), value)
                else:
                    command_dict['contents'] = add_to(command_dict.get('contents', ''), i)
        else:
            # 不进行高级检索，输入的字符串先放到command_dict中，因为可能是在进行复合检索
            command_dict['contents'] = command['contents']

            # 对应复合检索中，command还可能有title，author等key的情况，将它们提取出来
            for k, v in command.items():
                if k in allow_opt and v != '' and k not in command_dict:
                    command_dict[k] = v

        # 删除value 为''的内容。
        for k in list(command_dict.keys()):
            if command_dict[k] == '':
                del command_dict[k]
        return command_dict

    def query(self, command_dict, H_checked, p_checked) -> list:
        '''
            return a list of highlighted found results of the given query dict.
            Input: command_dict: dict or str.
            Return: res: list.
        '''

        # initialize
        command_dict = self.__parse_command(command_dict, H_checked)
        json_str = json.dumps(command_dict)
        result = self.cache.find(json_str)

        if result != None:
            return result

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

        self.cache.add(json_str, results)

        return results



if __name__ == '__main__':
    pass