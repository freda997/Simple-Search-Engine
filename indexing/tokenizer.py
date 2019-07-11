from bs4 import BeautifulSoup
import nltk
import re
from collections import Counter
from nltk.corpus import stopwords


def token_gen( path)->list:
    file = open(path, 'rb')
    file_content = file.read()
    file.close()
    raw_text = BeautifulSoup(file_content,
                             'html.parser')

    for script in raw_text.select('script'):
        script.decompose()
    for style in raw_text.select('style'):
        style.decompose()  # get rid of <script> and <style>

    text = raw_text.get_text()

    text = " ".join(re.findall("[a-zA-Z0-9@.-]+", text))  # get rid of all symbols and puntuation
    tokens = text.lower().split()

    # text= " ".join(re.findall("[a-zA-Z0-9]+", text))  #get rid of all symbols and puntuation
    # text=text.lower()
    # tokens = nltk.word_tokenize(text)

    return tokens

def token_stem( tokens:list) -> dict:
    stemmer = nltk.PorterStemmer()
    stem_tokens = []
    for t in tokens:
        stem_tokens.append(stemmer.stem(t))
    # print(dict(Counter(stem_tokens)))
    return dict(Counter(stem_tokens))

def string2tokens(s):
    sw = stopwords.words('English')
    text = " ".join(re.findall("[a-zA-Z0-9@.-]+", s))  # get rid of all symbols and puntuation
    tokens = text.lower().split()
    new_tokens =[t for t in tokens if t not in sw]
    return token_stem(new_tokens)

def get_snippets(path) -> str:
    file = open(path, 'rb')
    file_content = file.read()
    file.close()
    raw_text = BeautifulSoup(file_content,
                             'html.parser')

    for script in raw_text.select('script'):
        script.decompose()
    for style in raw_text.select('style'):
        style.decompose()  # get rid of <script> and <style>

    text = raw_text.get_text()
    snippet=text[0:200].replace('\n','')
    snippet=snippet.replace('\r','')
    return snippet+'...'