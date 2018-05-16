import re
import sqlite3
import os
import sys


def create_bd():
    conn = sqlite3.connect(os.path.join('.', 'main_bd13_SOS.sqlite'))
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS authors(id_author INTEGER PRIMARY KEY AUTOINCREMENT, author VARCHAR NOT NULL UNIQUE, url VARCHAR NOT NULL UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS poems_info(id_poem INTEGER PRIMARY KEY AUTOINCREMENT, poem_name VARCHAR NOT NULL, poem_url VARCHAR, author VARCHAR NOT NULL, year INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS poems(id_poem INTEGER PRIMARY KEY AUTOINCREMENT, poem_text TEXT UNIQUE, syllables VARCHAR)')
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx ON authors(author, url)')
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx2 ON poems_info(poem_name, poem_url)')
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx3 ON poems(id_poem, poem_text)')
    conn.commit()
    print('Таблицы созданы или уже существуют.')
    return


# poems_info: id, name, url, author
# authors: id, author, url
# poems: id_poem, poem_text, syllable
def infa():
    conn = sqlite3.connect(os.path.join('.', 'main_bd13_SOS.sqlite'))
    c = conn.cursor()
    file_list = os.listdir('poems')
    inf = {}
    for file_name in file_list:
        file_name = 'poems\\' + file_name
        with open(file_name, 'r', encoding='utf-8') as f:
            all = f.readlines()
        try:
            author = all[-204].split(':')[1].strip()
        except IndexError:  # тут один файл с ошибкой :(
            print('Error at ' + file_name)
            author = all[-205].split(':')[1].strip()
            print('Error solved.')
        name = all[16].split('~')[0].capitalize()
        url = all[0]
        if re.search('Puisi O|oleh', '\n'.join(all)) is None:
            print(file_name)
        poem_text_1 = '\n'.join(all[14:]).strip()
        poem_text_1 = '\n'.join(poem_text_1.split('\n')[1:]).strip()
        regex = re.compile('Puisi [Oo]leh.*', re.DOTALL)
        poem_text_2 = re.sub(regex, '', poem_text_1)
        c.execute('INSERT OR IGNORE INTO poems_info (poem_name, poem_url, author) VALUES (?, ?, ?)', [name, url, author])
        c.execute('INSERT OR IGNORE INTO poems (poem_text) VALUES (?)', [poem_text_2])
        conn.commit()
        print('Данные файла ' + file_name + ' добавлены в бд')


# create_bd()
# infa()


def navodim_losk():
    conn = sqlite3.connect(os.path.join('.', 'main_bd13_SOS.sqlite'))
    c = conn.cursor()
    c.execute('SELECT id_poem, poem_text FROM poems')
    for_change = c.fetchall()
    print(for_change)
    for i in for_change:
        print('Обновляем запись с id = ' + str(i[0]) + '...')
        try:
            c.execute('''UPDATE poems SET poem_text = '{}' WHERE id_poem = {}'''.format(re.sub('\"\"', '\"', i[1]).strip(), i[0]))
            conn.commit()
        except sqlite3.OperationalError:
            print('УПС... id = ' + str(i[0]))


# navodim_losk()


# ну такое...
def sth_stupid():
    conn = sqlite3.connect(os.path.join('.', 'main_bd13_SOS_shit.sqlite'))
    c = conn.cursor()
    c.execute('SELECT id_poem, poem_name FROM poems_info')
    infa = c.fetchall()
    for i in infa:
        id = i[0]
        name = i[1]
        c.execute('''UPDATE poems SET poem_name = '{}' WHERE id_poem = {}'''.format(name, str(id)))
    conn.commit()


sth_stupid()
