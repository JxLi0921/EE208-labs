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
                    filename_1: (url_1, title_1),
                    filename_2: (url_2, title_2),
                    ......
                }
        '''
        info_path = r'cleaned_file_index.txt'
        info = {}

        with open(info_path, 'r', encoding='utf-8') as info_file:
            lines = info_file.readlines()
            for line in lines:
                try:
                    file_name, orig_url, title = tuple(line.split(' ', 2))
                    info[file_name] = orig_url, title
                except:
                    continue
        
        return info


    def __init__(self, root, storeDir):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        # store = SimpleFSDirectory(File(storeDir).toPath())
        self.info = self.read_info()
        self.log_file = open('index_log.txt', 'w', encoding='utf-8')

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

        self.log_file.close()

    def indexDocs(self, root, writer):

        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed

        t3 = FieldType()
        t3.setStored(True)
        t3.setTokenized(False)
        t3.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Not Indexed
        
        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexes documents, frequencies and positions.
        i = 0
        orig_root = 'htmls'

        for root, dirnames, filenames in os.walk(root):
            tot = len(filenames)
            for filename in filenames:
                # For each filename, create a document, and add the name, url, title and path to it.
                # Then add the document to the indexWriter.
                if not filename.endswith('.txt'):
                    continue
                print(f"{i+1}/{tot} adding", filename)
                i+=1
                filename = filename.replace('.txt', '.html')
                try:
                    path = os.path.join(orig_root, filename)
                    file = open(path, encoding='utf-8')
                    contents = file.read()
                    file.close()
                    doc = Document()
                    doc.add(Field("name", filename, t3))
                    url, title = self.info[filename]
                    doc.add(Field("url", url[2:-1], t3))
                    doc.add(Field("title", title, t3))
                    doc.add(Field("path", path, t1))
                    doc.add(Field("site", self.url_to_site(url[2:-1]), t3))
                    if len(contents) > 0:
                        doc.add(Field("contents", contents, t2))
                    else:
                        print("warning: no content in %s" % filename)
                        self.log_file.write("warning: no content in {}".format(filename))
                    writer.addDocument(doc)
                except Exception as e:
                    print(e)
                    print("Failed in indexDocs:", e)


if __name__ == '__main__':
    lucene.initVM()#vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    # import ipdb; ipdb.set_trace()
    start = datetime.now()
    try:
        IndexFiles('cleaned_htmls', "my_index") 
        # all new html files are in `cleaned_htmls` folder, 
        # create corresponding index file in the folder `my_index`
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e