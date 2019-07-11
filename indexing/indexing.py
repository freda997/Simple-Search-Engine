
from corpus import Corpus

from tokenizer import token_stem
from tokenizer import token_gen
from DataBase import create_table

import math
class indexer:
    def __init__(self,session):
        self.corpus=Corpus()
        self.session=session

    def show_page_content(self):
        f=open('pages2.txt','w')
        cur=self.session.cursor()
        f.write("************************pages\n")

        cur.execute('''SELECT * FROM pages''')
        for row in cur:
            f.write(str(row)+'\n')

        f.close()

    def show_token_content(self):
        f = open('tokens2.txt', 'w')
        cur = self.session.cursor()

        f.write("************************tokens\n")
        cur.execute('''SELECT * FROM tokens''')
        c=0
        for row in cur:
            f.write(str(row)+'\n')
            c+=1
        f.write("number of rows returned: "+str(c))
        f.close()

    def show_index_content(self):
        f=open('indices2.txt','w')
        cur=self.session.cursor()
        f.write("************************indexing\n")

        cur.execute('''SELECT * FROM indexing''')
        c=0
        for row in cur:
            f.write(str(row)+'\n')
            c+=1
        f.write("number of rows returned: "+str(c))
        f.close()

    def test(self):
        cur=self.session.cursor()
        create_table(cur)
        # url="graphmod.ics.uci.edu/group/aolibILP?action=login"
        # page_path = self.corpus.get_file_name(url)
        # tokens_dict = self.token_stem(self.token_gen(page_path))
        index_list=[]
        page_path = self.corpus.get_file_name("www.ics.uci.edu/community/news/articles/view_article?id=344")
        tokens_dict = token_stem(token_gen(page_path))
        for token, freq in tokens_dict.items():
            index_list.append((token, 4, freq))
        cur.executemany("INSERT INTO indexing (token,page_id,token_freq) VALUES(?,?,?)", index_list)
        self.session.commit()
        index_list.clear()

    def create_pages(self,cur):
        keys=self.corpus.url_file_map.keys()
        page_list=zip(range(len(keys)),keys)
        cur.executemany("INSERT INTO pages VALUES (?,?)",list(page_list))
        self.session.commit()
        self.show_page_content()

    def start_indexing(self):
        cur=self.session.cursor()
        create_table(cur)
        #self._create_pages(cur)
        page_id = 0
        index_list=[]
        for url in self.corpus.url_file_map.keys():
            print(url)
            page_path=self.corpus.get_file_name(url)
            tokens_dict=token_stem(token_gen(page_path))
            for token,freq in tokens_dict.items():
                tf_score = 1 + math.log10(freq)
                cur.execute("SELECT doc_freq FROM tokens WHERE tokens.token=? LIMIT 1", (token,))
                df = cur.fetchall()
                idf_score = math.log10(37497 / (df[0][0]))
                score=tf_score*idf_score
                print((token,page_id,freq,score))
                index_list.append((token,page_id,freq,score,))

            if len(index_list)>1000000:
                cur.executemany("INSERT INTO indexing (token,page_id,token_freq,tf_idf) VALUES(?,?,?,?)", index_list)
                self.session.commit()
                index_list.clear()
            page_id += 1
        cur.executemany("INSERT INTO indexing (token,page_id,token_freq,tf_idf) VALUES(?,?,?,?)", index_list)
        self.session.commit()
        index_list.clear()
        #self.calculate_tf_idf()

    def calculate_tf_idf(self):
        cur=self.session.cursor()

        cur.execute("SELECT token,page_id,token_freq,tf_idf FROM indexing")
        update_list=[]
        for token,page_id,tf,score in cur.fetchall():
            if score==None:
                tf_score=1+math.log10(tf)
                cur.execute("SELECT doc_freq FROM tokens WHERE tokens.token=? LIMIT 1",(token,))
                df=cur.fetchall()
                idf_score=math.log10(37497/(df[0][0]))  #log(N/df)
                print((tf_score*idf_score,token,page_id,))
                update_list.append((tf_score*idf_score,token,page_id))
                if len(update_list)>1000000:
                    cur.executemany("UPDATE indexing SET tf_idf=? WHERE token= ? AND page_id = ?",update_list)
                    update_list.clear()
                    self.session.commit()
        cur.executemany("UPDATE indexing SET tf_idf=? WHERE token= ? AND page_id = ?", update_list)
        update_list.clear()
        self.session.commit()








