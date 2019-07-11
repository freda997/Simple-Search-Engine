from tokenizer import string2tokens
import math
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import operator
from corpus import Corpus
from tokenizer import get_snippets
URLS_DISPLAYED=10
FREQUENCY_THREDSHOLD=5
import time
class Searcher:
    def __init__(self,cur,q):
        self.query=q
        self.cursor=cur
        self.corpus=Corpus()
        #self.start_searching()
        self.urls=[]
        self.results=[]
        self.read_pos=0
        self.q_dict=string2tokens(self.query)
        start=time.time()
        scores = self.cos_score(self.select_doc(FREQUENCY_THREDSHOLD))
        print(" building scores takes --- %s seconds ---" % (time.time() - start))
        self.scores = sorted(scores.items(), reverse=True, key=operator.itemgetter(1))
        self.start_searching()

    def select_doc(self,min_freq):
        '''Select documents that contain at least one query term. '''
        docs=set()
        for term in self.q_dict.keys():
            temp_freq = min_freq
            while True:

                matched_docs = 0
                self.cursor.execute("SELECT page_id FROM indexing WHERE token=? AND token_freq>=?",(term,temp_freq))
                all_pages=self.cursor.fetchall()
                for pid, in all_pages:
                    docs.add(pid)
                    matched_docs+=1
                if matched_docs>20 or temp_freq==1:
                    break
                else:
                    temp_freq-=1


            # new_docs=dict((k,v) for k,v in docs.items() if v>len(self.q_dict)/3)
        # if len(docs)<20:
        #     if min_freq>1:  #reduce min_freq to get more url results
        #         docs=self.select_doc(min_freq-1)
        return docs
    def _term_score(self,term):
        self.cursor.execute("SELECT doc_freq FROM tokens WHERE token=? LIMIT 1", (term,))
        return (1 + math.log10(self.q_dict[term])) * math.log10(37497 / self.cursor.fetchall()[0][0])

    def buildVector(self,doc:int):
        '''gvien a page number and generate a vector for that page'''
        self.cursor.execute("SELECT token,tf_idf FROM indexing WHERE page_id=? ", (doc,))

        doc_record=self.cursor.fetchall()
        doc_vector={}
        query_vector = {}
        for token,score in doc_record:
            doc_vector[token]=score
            query_vector[token]=0
        query_terms=self.q_dict.keys()
        for term in query_terms:
            if term not in query_vector:
                doc_vector[term]=0
            query_vector[term]= self._term_score(term)
        assert len(doc_vector)==len(query_vector)
        return [list(doc_vector.values()),list(query_vector.values())]

    def cos_score(self,docs:set):
        scores={}
        for doc in docs:
            dv,qv=self.buildVector(doc)
            ndv=np.array(dv).reshape(1,len(qv))
            nqv=np.array(qv).reshape(1,len(dv))
            score=cosine_similarity(ndv,nqv)
            score=score[0][0]
            scores[doc]=score
        return scores

    def results_gen(self) -> list:
        '''generate query result from given starting postion. Result : [(url,text_snippet),(...)]'''
        if self.read_pos>=len(self.results):
            self.generate_urls(self.read_pos)
            for i in range(self.read_pos,self._end_score(self.read_pos+URLS_DISPLAYED)):
                snippet=get_snippets(self.corpus.get_file_name(self.urls[i]))
                self.results.append((self.urls[i],snippet,))
        temp_result = self.results[self.read_pos:self._end_score(self.read_pos + URLS_DISPLAYED)]
        return temp_result
    def _end_score(self,end:int):
        if end>len(self.scores):
            return len(self.scores)
        return end
    def generate_urls(self,start) :
        result_list = []
        for pid,score in self.scores[start:self._end_score(start+URLS_DISPLAYED)]:
            self.cursor.execute("SELECT url FROM pages WHERE page_id=? ", (pid,))
            url = self.cursor.fetchall()[0][0]
            result_list.append(url)
        self.urls=self.urls+result_list

    def start_searching(self) :
        f=open("searches_result.txt",'a')
        # scores=self.cos_score(self.select_doc())
        # scores=sorted(scores.items(),reverse=True,key=operator.itemgetter(1))
        result_list=[]
        f.write("***********Search Results for \'"+self.query+"\': "+str(len(self.scores))+" urls found *****************\n")
        for pid,score in self.scores[0:20]:
            self.cursor.execute("SELECT url FROM pages WHERE page_id=? ", (pid,))
            url = self.cursor.fetchall()[0][0]
            #print(str(self.corpus.get_file_name(url)),score,url)
            f.write(url+'\n')
            result_list.append(url)
        f.write('\n\n')
        f.close()
