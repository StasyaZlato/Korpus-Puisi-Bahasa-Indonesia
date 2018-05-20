import re
import sqlite3
import os
import json


def take_alll():
    conn = sqlite3.connect(os.path.join('.', 'KorpusBD.sqlite'))
    c = conn.cursor()
    c.execute('SELECT id_poem, poem_text FROM poems')
    all = c.fetchall()
    dic = {}
    for i in all:
        dic[i[0]] = i[1]
    return dic


def count_words():
    all = take_alll().values()
    words = 0
    for i in all:
        text = i.split()
        words += len(text)
    print(words)

count_words()


def count_syllables(line):
    line_new = re.sub('(ai)|(au)|(oi)', 'γ', line)
    regex = re.compile('a|e|i|o|u|γ')
    syllables = len(re.findall(regex, line_new))
    return syllables


def parsing_syllables(text, id):
    conn = sqlite3.connect(os.path.join('.', 'authors.sqlite'))
    c = conn.cursor()
    a = {}
    # a = {1:2, 3:4}
    # d = json.dumps(a)
    strs = text.split('\n')
    for i in range(len(strs)):
        try:
            strs.remove('')
        except ValueError:
            break
    for i in range(len(strs)):
        syls = count_syllables(strs[i])
        a[i] = syls
    d = json.dumps(a)
    c.execute('CREATE TABLE IF NOT EXISTS poems_new (id_poem INTEGER PRIMARY KEY UNIQUE, poem_text TEXT UNIQUE, syllables TEXT)')
    # c.execute('INSERT INTO poems_new (id_poem, poem_text) SELECT id_poem, poem_text FROM poems')
    c.execute('UPDATE poems_new SET syllables=(?) WHERE id_poem=(?)', (d, id))
    conn.commit()


'''201 929 слов!!! каееееееф:)))'''


# def dic_indonesian():
#     dic = {}
#     files_list = os.listdir(r'C:\Users\User\Documents\progs2\teks')
#     others = []
#     for file in files_list:
#         with open(os.path.join(r'C:\Users\User\Documents\progs2\teks', file), 'r', encoding='utf-8') as f:
#             words = f.readlines()
#             for word in words:
#                 try:
#                     li = word.split('\t')[0:2]
#                     dic[li[0]] = li[1]
#                 except IndexError:
#                     others.append(word)
#                     continue
#     return dic

def dic_indonesian():
    with open('kbbi_kak_zhe_ia_s_nim_zadolbalas.txt', 'r', encoding='utf-8') as f:
        dictionary_prev = f.readlines()
    regex = re.compile(' / (\w{1,4}) /')
    dict_plain = {}
    dict_transform = {}
    for line in dictionary_prev:
        if re.search(regex, line) is not None:
            line = line.strip()
            line = line.replace('\ufeff', '')
            line1 = line.split('/')
            parts_with_om = re.findall(regex, line)
            parts_with_om_copy = []
            for i in parts_with_om:
                if i not in parts_with_om_copy:
                    parts_with_om_copy.append(i)
            dict_plain[line1[0]] = parts_with_om_copy
        else:
            if re.search('-->', line) is not None:
                line = line.strip()
                line1 = line.split('-->')
                dict_transform[line1[0]] = line1[1]
    return dict_plain, dict_transform


def main():
    poems = take_alll()
    for id, text in poems.items():
        print(id)
        parsing_syllables(text, id)


def parse_with_partsofspeech(text):
    lines = text.split('\n')
    regex = re.compile('(\w+-?\w*)\W')
    dict1, dict2 = dic_indonesian()
    print(dict1)
    print(dict2)
    text_new = []
    for line in lines:
        print(line)
        line_new = line.lower()
        words1 = re.findall(regex, line_new)
        print(words1)
        words = []
        for word1 in words1:
            if word1 not in words:
                words.append(word1)
        for word in words:
            if word in dict1.keys():
                part_of_speech = ' '.join(dict1[word])
            # elif word not in dict.keys() and word.endswith('ku'):
            else:
                part_of_speech = '?'
            line = re.sub(word, word+'{' + part_of_speech + '}', line)
        text_new.append(line)
    print('\n'.join(text_new))

# main()


# poem = '''Ibuku dehulu marah padaku
# diam ia tiada berkata
# akupun lalu merajuk pilu
# tiada peduli apa terjadi
#
# matanya terus mengawas daku
# walaupun bibirnya tiada bergerak
# mukanya masam menahan sedan
# hatinya pedih kerana lakuku
#
# HTerus aku berkesal hati
# menurutkan setan, mengkacau-balau
# jurang celaka terpandang di muka
# kusongsong juga - biar chedera
#
# Bangkit ibu dipegangnya aku
# dirangkumnya segera dikucupnya serta
# dahiku berapi pancaran neraka
# sejuk sentosa turun ke kalbu
#
# Demikian engkau;
# ibu, bapa, kekasih pula
# berpadu satu dalam dirimu
# mengawas daku dalam dunia.
# '''
# parse_with_partsofspeech(poem)