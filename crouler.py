import urllib.request
import re
import sqlite3
import os
import sys



def create_bd():
    conn = sqlite3.connect(os.path.join('.', 'main_bd13_SOS.sqlite'))
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS authors(id_author INTEGER PRIMARY KEY AUTOINCREMENT, author VARCHAR NOT NULL UNIQUE, url VARCHAR NOT NULL UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS poems_info(id_poem INTEGER PRIMARY KEY AUTOINCREMENT, poem_name VARCHAR NOT NULL, poem_url VARCHAR, author VARCHAR NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS poems(id_poem INTEGER PRIMARY KEY UNIQUE, poem_text TEXT UNIQUE, vowels INTEGER)')
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx ON authors(author, url)')
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx2 ON poems_info(poem_name, poem_url)')
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx3 ON poems(id_poem, poem_text)')
    conn.commit()
    print('Таблицы созданы или уже существуют.')
    return


def download(pageUrl):
    try:
        page = urllib.request.urlopen(pageUrl) # берем страницу
        html = page.read().decode('utf-8') # достаем html
        print('Страница {} скачана.'.format(pageUrl))
        return html
    except:
        print('Error at ', pageUrl)
        sys.exit()


def del_html(html_text):
    import html
    html_text = html.unescape(html_text)
    return html_text


def all_urls_authors(html_text):
    regex = re.compile('<ul>.*?</ul>', re.DOTALL)
    urls = re.findall(regex, html_text)
    authors_html = urls[2]
    regex = re.compile('<a.*?>.*?</a>', re.DOTALL)
    authors_wt = re.findall(regex, authors_html)
    authors = {}
    regex_url = re.compile('<a.*?href=\'(.*?)\'>', re.DOTALL)
    regex_name = re.compile('<a.*?>(.*?)</a>', re.DOTALL)
    for i in authors_wt:
        a = re.search(regex_name, i).group(1)
        b = re.search(regex_url, i).group(1)
        authors[a] = b
    print('Словарь авторов создан.')
    return authors


def table_authors(authors: dict):
    conn = sqlite3.connect(os.path.join('.', 'authors.sqlite'))
    c = conn.cursor()
    for k, v in authors.items():
        c.execute('INSERT OR IGNORE INTO authors (author, url) VALUES (?, ?)', [k, v])
    conn.commit()
    print('Таблица authors заполнена.')
    return


def main1():
    create_bd()
    url = 'http://www.puisikita.com/search/label/Ajip%20Rosidi?updated-max=2010-11-01T21:46:00-07:00&max-results=20&start=20&by-date=false'
    html_text = del_html(download(url))
    authors = all_urls_authors(html_text)
    table_authors(authors)
    print('Main1 выполнено')
    return authors


def poems_of_author():
    conn = sqlite3.connect(os.path.join('.', 'authors.sqlite'))
    c = conn.cursor()
    c.execute('SELECT author, url FROM authors')
    urls = c.fetchall()
    print('Ссылки из базы данных извлечены.')
    return urls


def find_poems(html_text):
    regex1 = re.compile('<h3.*?><a href=\'(.*?)\'>(.*?)</a></h3>', re.DOTALL)
    regex2 = re.compile('<a class=\'blog-pager-older-link\' href=\'(.*?)\'.*?>Older Posts</a>', re.DOTALL)
    poems = {}
    while True:
        try:
            list_buf = re.findall(regex1, html_text)
            for i in list_buf:
                ref = i[0]
                name = i[1].split('~')
                for k in range(len(name)):
                    if name[k].startswith(' '):
                        name[k] = name[k][1:]
                    if name[k].endswith(' '):
                        name[k] = name[k][:-1]
                    name[k] = name[k].capitalize()
                poems[tuple(name)] = ref
            next = re.search(regex2, html_text).group(1)
            html_text = download(next)
        except AttributeError:
            break
    print('Словарь стихотворений создан.')
    return poems


def table_poems_info(poems: dict, author):
    conn = sqlite3.connect(os.path.join('.', 'authors.sqlite'))
    c = conn.cursor()
    for k, v in poems.items():
        c.execute('INSERT OR IGNORE INTO poems_info (poem_name, poem_url, author) VALUES (?, ?, ?)', [k[0], v, author])
    conn.commit()
    print('Таблица poems_info заполнена.')


def main2():
    urls = poems_of_author()
    for url in urls:
        print(url)
        html_text = del_html(download(url[1]))
        urls1 = find_poems(html_text)
        print(urls1)
        table_poems_info(urls1, url[0])
    print('Main2 выполнено.')


def poem_urls():
    conn = sqlite3.connect(os.path.join('.', 'authors.sqlite'))
    c = conn.cursor()
    c.execute('SELECT id_poem, poem_url FROM poems_info')
    poems = c.fetchall()
    regex = re.compile('<div class=\'post-body entry-content\'>(.*?)<span', re.DOTALL)
    poems_dict = {}
    for poem in poems:
        try:
            id = poem[0]
            url = poem[1]
            html_text = download(url)
            try:
                html_text = del_html(html_text)
            except Exception as error:
                print('А страничка-то ' + url + ' не скачана!')
                with open('DelErrors.txt', 'a', encoding='utf-8') as k:
                    k.write('url: ' + poem[1] + '\terror: ' + str(error) + '\n')
                continue
            regex_script = re.compile('<script.*?>.*?</script>', re.DOTALL)
            html_text = re.sub(regex_script, '', html_text)
            regex_style = re.compile('<style.*?>.*?</style>', re.DOTALL)
            html_text = re.sub(regex_style, '', html_text)
            regex_head = re.compile('<head>.*?</head>', re.DOTALL)
            html_text = re.sub(regex_head, '', html_text)
            html_text = re.sub('<br />\n*', '\n', html_text)
            regex_tags_all = re.compile('<.*?>', re.DOTALL)
            html_text_wt = re.sub(regex_tags_all, '', html_text)
            html_text_wt = re.sub('\n+', '\n', html_text_wt)
            with open(os.path.join('.', 'poems\\{}.txt'.format(str(id))), 'w', encoding='utf-8') as file:
                file.write(url + '\n')
                file.write(html_text_wt)
        except Exception as error:
            print('!!!!!!! Я щас сдохну. Честно.!!!!!!!')
            with open('CriticalErrors.txt', 'a', encoding='utf-8') as k:
                k.write('url: ' + poem[1] + '\terror: ' + str(error) + '\n')
    return poems_dict


def poems_clean(f):
    with open('.\\poems\\' + f, 'r', encoding='utf-8') as k:
        text = k.readlines()
        text1 = '\n'.join(text[15:-204]).strip()
        text_only = text1.split('\n')[1:]
        text_only_final = '\n'.join(text_only)
        return text_only_final


def table_poems():
    conn = sqlite3.connect(os.path.join('.', 'authors.sqlite'))
    c = conn.cursor()
    files_list = os.listdir(r'C:\Users\User\Documents\progs2\poems')
    for f in sorted(files_list):
        id = f[:-4]
        text = poems_clean(f)
        c.execute('INSERT OR IGNORE INTO poems (id_poem, poem_text) VALUES (?, ?)', [id, text])
        conn.commit()
    print('Таблица poems заполнена.')


def main3():
    poem_urls()
    table_poems()
    print('Main3 выполнено.')


def proverka(i):
    conn = sqlite3.connect(os.path.join('.', 'authors.sqlite'))
    c = conn.cursor()
    c.execute('SELECT poem_text FROM poems')
    a = c.fetchall()
    print(a[i][0])


main1()
main2()
main3()