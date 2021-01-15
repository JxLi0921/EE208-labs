import sys, os, lucene, threading, time
from datetime import datetime

# from java.io import File
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.cjk import CJKAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StringField
from org.apache.lucene.index import FieldInfo, Term, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)


class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def url_to_site(self, s):
        start_index = 0
        while (s[start_index] != '/'):
            start_index += 1
        start_index += 2
        end_index = start_index
        while (end_index < len(s) and s[end_index] != '/'):
            end_index += 1
        return s[start_index : end_index]

    def read_info(self):
        '''
            Used to read the information from the index file.
            return: 
                a dict, which will be like this: {
                    fileid_1: tup1,
                    fileid_2: tup2,
                    ......
                }
        '''
        info_path = r'index_pic.txt'
        info = {}

        with open(info_path, 'r', encoding='utf-8') as info_file:
            lines = info_file.readlines()
            
            for line in lines:
                try:
                    file_id, title, author, photography, source, img_address, url = tuple(line.split(' '))
                    info[file_id] = title, author, photography, source, img_address, url
                except Exception as e:
                    print(e)
                    continue
        
        return info


    def __init__(self, root, storeDir):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        # store = SimpleFSDirectory(File(storeDir).toPath())
        self.info = self.read_info()

        store = SimpleFSDirectory(Paths.get(storeDir))
        analyzer = CJKAnalyzer()
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocs(root, writer)
        ticker = Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

    def indexDocs(self, root, writer):

        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed

        t3 = FieldType()
        t3.setStored(True)
        t3.setTokenized(True)
        t3.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexed and stored.
        
        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexes documents, frequencies and positions.
        i = 0

        for key, value in self.info.items():
            i += 1
            print('current task:', i)
            title, author, photography, source, img_address, url = value
            
            passage_file = None
            try:
                passage_file = open('passages/' + key + '.txt', 'r', encoding='utf-8')
            except:
                continue
            passage = passage_file.read()
            passage_file.close()

            # add fields to the new document
            doc = Document()
            doc.add(Field("title", title, t3))
            doc.add(Field("url", url, t3))
            doc.add(Field("id", key, t3))
            # 'None' means that the passage does not have this information.
            if author != "None":
                doc.add(Field("author", author, t3))
            if photography != "None":
                doc.add(Field("photography", photography, t3))
            if source != "None":
                doc.add(Field("source", source, t3))
            doc.add(Field("imgaddr", img_address, t3))
            doc.add(Field("url", url, t3))
            doc.add(Field("contents", passage, t3))
            writer.addDocument(doc)


if __name__ == '__main__':
    lucene.initVM()#vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    # import ipdb; ipdb.set_trace()
    start = datetime.now()
    try:
        IndexFiles('passages', "pic_index_2") 
        # all new html files are in `cleaned_htmls` folder, 
        # create corresponding index file in the folder `my_index`
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e