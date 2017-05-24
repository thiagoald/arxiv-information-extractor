import regex
import codecs
import simplejson as json
import unicodedata

def main():
    with codecs.open('documents/docs.txt', 'r') as f:
        text = unicodedata.normalize("NFKD", f.read().decode('utf-8'))
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
                   'abstract':m.group(13)
                  }
        all_articles.append(article)
    json.dump(all_articles, codecs.open('resource/output/articlesFromDoc.json', 'w', 'utf-8'), indent='  ', ensure_ascii=False)
if __name__ == "__main__":
    main()