import regex
import codecs
import simplejson as json
import unicodedata

import nltk
from pycorenlp import *
import collections


def main():
    with codecs.open('documents/docs.txt', 'r') as f:
        text = unicodedata.normalize("NFKD", f.read().decode('utf-8'))
    
    #start the nlp server:
    nlp=StanfordCoreNLP("http://localhost:9000/")
    
    # print text
    all_articles = []
    for m in regex.finditer(r"\n\[?\d+\]?\s*arXiv:(\d*\.\d*).*\n(.*)\n(.*)\n((Comments:\s)(.*)\n)?((Journal-ref:)(.*)\n)?((Subjects:)(.*)\n)?(.*)", text):
        print m.group(0).encode('ascii', 'ignore')
        article = {'id':m.group(1),
                   'title':m.group(2),
                   'authors':m.group(3).split(','),
                   'comments':m.group(6),
                   'journalRef':m.group(9),
                   'subjects':m.group(12).split(';'),
                   'abstract':m.group(13),
                   'relations': []
                  }
        s = str(article['abstract'])
        output = nlp.annotate(s, properties={"annotators":"tokenize,ssplit,pos,depparse,natlog,openie",
                                "outputFormat": "json",
                                 "openie.triple.strict":"true",
                                 "openie.max_entailments_per_clause":"1",
                                 "splitter.disable":"true"})
        result = [output["sentences"][0]["openie"] for item in output]
        relations = []
        for i in result:
            for rel in i:
                relationSent = rel['subject'],rel['relation'],rel['object']
                relations.append(relationSent)
        article['relations'] = relations
        
        all_articles.append(article)
    json.dump(all_articles, codecs.open('documents/articlesFromDoc.json', 'w', 'utf-8'), indent='  ', ensure_ascii=False)
if __name__ == "__main__":
    main()