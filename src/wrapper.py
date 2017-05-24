import os
import traceback
import codecs

import bs4
import simplejson as json
import requests

def extract_articles(html_string):
    ''' Extracts a list of articles from a html string
    '''
    all_articles = []
    soup = bs4.BeautifulSoup(html_string, 'html.parser')
    all_dds = []
    all_dts = []
    for dl_tag in soup.find_all('dl'):
        for dd_tag in dl_tag.find_all('dd'):
            all_dds.append(dd_tag)
        for dt_tag in dl_tag.find_all('dt'):
            all_dts.append(dt_tag)

    print 'Found', len(all_dds), 'articles!'
    for article_content, article_link in zip(all_dds, all_dts):
        article = {'title':'',
                   'authors':[],
                   'subjects':{
                       'primary':'',
                       'others':[]
                       },
                   'abstract':''
                  }
        meta_tag = article_content.find('div', class_='meta')

        # Title
        try:
            title_tag = meta_tag.find('div', class_='list-title mathjax')
            article['title'] = title_tag.contents[-1]
        except Exception as e:
            print 'ERROR! Could not extract title!"'
            print traceback.format_exc()

        # Authors
        try:        
            authors_tag = meta_tag.find('div', class_='list-authors')
            for author_tag in authors_tag.find_all('a'):
                article['authors'].append(author_tag.contents[0])
        except Exception as e:
            print 'ERROR! Could not extract authors for "', article['title'], '"!'
            print traceback.format_exc()

        # Primary subject
        subjects_tag = meta_tag.find('div', class_='list-subjects')
        try:
            article['subjects']['primary'] = subjects_tag.find('span', class_='primary-subject').contents[0]
        except Exception as e:
            print 'ERROR! Could not extract primary subject for "', article['title'], '"!'
            print traceback.format_exc()

        # Other subjects
        try:
            if subjects_tag.contents[-1] != '\n':
                article['subjects']['others'] = [subject for subject in subjects_tag.contents[-1].split(';') if subject != '']
        except Exception as e:
            print 'ERROR! Could not extract other subjects for "', article['title'], '"!'
            print traceback.format_exc()

        # Abstract
        try:
            article['abstract'] = meta_tag.find('p').contents[0]
        except Exception as e:
            print 'ERROR! Could not extract abstract for "', article['title'], '"!'
            print traceback.format_exc()
        
        all_articles.append(article)

    return all_articles

if __name__ == "__main__":

    URL = 'https://arxiv.org/list/quant-ph/new'
    html_text = None

    # Creating folder structure
    if 'resource' not in os.listdir('.'):
        print 'Resource folder not found! Creating...'
        os.mkdir('resource')
        os.mkdir('resource/input')
        os.mkdir('resource/output')
        print 'Done!'

    if 'input' not in os.listdir('./resource'):
        print 'Input folder not found! Creating...'
        os.mkdir('resource/input')
        print 'Done!'

    if 'output' not in os.listdir('./resource'):
        print 'Output folder not found! Creating...'
        os.mkdir('resource/output')
        print 'Done!'

    # Checking if html file was downloaded
    if 'htmlFile.html' in os.listdir('resource/input'):
        print 'Opening resource/input/htmlFile.html...'
        with codecs.open('resource/input/htmlFile.html', 'r', 'utf-8') as f:
            html_text = f.read().decode('utf-8')
    else:
        print 'Requesting html...'
        try:
            r = requests.get(URL)
            html_text = r.text.decode('utf-8')
            print 'Request successful!'
            with codecs.open('resource/input/htmlFile.html', 'w', 'utf-8') as f:
                print 'Creating resource/input/htmlFile.html...'
                f.write(html_text)
            print 'Done!'
        except Exception as e:
            print 'ERROR! Could not request html!'
            print e

    if html_text is not None:
        print 'Extracting articles...'
        articles = extract_articles(html_text)
        print 'Done!\n'
        print 'Generating output file (resource/output/articlesFromHTML.json)...'
        json.dump(articles, codecs.open('resource/output/articlesFromHTML.json', 'w', 'utf-8'), indent='  ', ensure_ascii=False)
        print 'Done!\n'