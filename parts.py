import re
import download_module as down
from bs4 import BeautifulSoup as bs
import json
import os



# LIST_JSON = {}

# первое действие - открытие файла под чтение для проверки наличия в нем слова.
# Это можно только на существующем файле.

# with open('DICTIONARY.txt', 'a', encoding='utf-8') as k:
#     k.write('')


def take_word_page(word):
    html = down.download('https://kbbi.web.id/' + word.lower())
    if html is None:
        print('Сорян, слово не найдено! Печалька :(')
    else:
        with open(r'html_changing.txt', 'w', encoding='utf-8') as f:
            f.write(down.del_html(html.replace('&#183;', '')))
        return down.del_html(html.replace('&#183;', ''))


def changing_terms(new_list):
    for i in range(len(new_list)):
        word = new_list[i][0]
        word = [k for k in word if re.search('[^a-zA-Z-]', k) is None and re.search('\w', k) is not None]  # слово может состоять ТОЛЬКО из букв и дефиса.
        word = [l for l in word if re.search('\d', l) is None and l != '']
        word = [l for l in word if len(l) > 1]
        new_list[i][0] = word
    indexes_reverse = [num for num in range(len(new_list))]
    indexes_reverse.reverse()
    for i in indexes_reverse:
        if not new_list[i][0]:
            try:
                new_list[i-1][1].extend(new_list[i][1])
            except IndexError:
                print('Кажется, список закончился?..')
    return new_list


def changing_parts(new_list):
    parts_list = ['n', 'v', 'pron', 'adv', 'a', 'num', 'p']
    for i in range(len(new_list)):
        parts0 = new_list[i][1]
        parts = []
        for part in parts0:
            parts.extend(part.split(' '))
        parts = [part.strip(',.-;:?! ') for part in parts]
        index = 0
        while index + 1 <= len(parts):
            part = parts[index]
            part = part.strip(',.-;:?! ')
            if part not in parts_list:
                parts.remove(part)
            else:
                index += 1
        parts1 = []
        for part in parts:
            if part not in parts1:
                part = part.strip(',.-;:?! ')
                parts1.append(part)
        new_list[i][1] = ['|'.join(parts1)]
    return new_list


def word_inf(html):
    html = re.sub('<sup>.*?</sup>', '', html)
    soup = bs(html, 'lxml')
    container = soup.find('div', {'id': 'd1'})
    needed = str(container)
    a = re.findall('(<b>.*?</b>)+\s*(<em>.*?</em>)+', needed, re.DOTALL)
    new_list = []
    for i in a:
        new_new = []
        for item in i:
            sth = re.split('<[a-z/]*>', item)
            sth = [l.strip() for l in sth]
            new_new.append(sth)
        new_list.append(new_new)
    for i in new_list:
        for item in i:
            for item1 in item:
                if item1 == '' or item1 == ' ':
                    item.remove(item1)
    new_list = changing_terms(new_list)
    new_list = changing_parts(new_list)
    new_list = [new_list[i] for i in range(len(new_list)) if new_list[i][0] != []]
    return new_list


def check_roots(new_list, word):
    dict_1 = {tuple(words[0]): words[1] for words in new_list}
    dict_2 = dict_1.copy()
    for key in dict_1.keys():
        if len(key) > 1:
            for i in key:
                dict_2[tuple([i])] = dict_2[key]
            dict_2.pop(key)
    list_of_words = dict_2.keys()
    checked = []
    for i in list_of_words:
        for n in i:
            if word.lower() in n.lower() or n.lower() in word.lower() or n[1:] in word:
                checked.append(n)
            elif word.lower().startswith('pe') or word.lower().startswith('me') or word.lower().startswith('ke') or word.lower().startswith('be') or word.lower().startswith('ter'):
                for l in range(len(word)-3):
                    if word[l:] in n.lower():
                        checked.append(n)
                        break
            elif n.lower().startswith('pe') or n.lower().startswith('me') or n.lower().startswith('ke') or n.lower().startswith('be') or n.lower().startswith('ter'):
                for l in range(len(n)-3):
                    if n[l:] in word.lower():
                        checked.append(n)
                        break
            else:
                print(word + ' ~ ' + n + ' ~~ NO')
    new_list_of_lists = [[[check], dict_2[tuple([check])]] for check in checked]
    return new_list_of_lists


def add_to_dict(list_parts):
    with open('DICTIONARY.txt', 'r', encoding='utf-8') as f:
        dict_parts = f.readlines()
    with open('DICTIONARY.txt', 'a', encoding='utf-8') as f:
        for i in list_parts:
            line_got = i[0][0] + '\t' + i[1][0] + '\n'
            if line_got not in dict_parts:
                f.write(line_got)


def search_in_file(word):
    with open('DICTIONARY.txt', 'r', encoding='utf-8') as f:
        dictionary = f.read()
    for line in dictionary.splitlines():
        if word + '\t' in line or word.lower() + '\t' in line:
            part = line.split('\t')[1]
            return part
    if word + '\t' not in dictionary:
        return None


def if_not_found(word):
    if '-' in word and (re.search(word.lower().split('-')[1], word.lower().split('-')[0]) is not None or re.search(word.lower().split('-')[0], word.lower().split('-')[1]) is not None):
        word = word.split('-')[0]
        if search_in_file(word) is not None:
            print('Word ~ in dict')
            return {word: search_in_file(word)}
        elif take_inf(word):
            part = if_list_checked(take_inf(word), word)
            return {word: part}
    if (word.lower().startswith('me') is True and word.lower().startswith('memper') is False) or word.startswith('ber'):
        word = {word: 'v'}
        return word
    elif word.endswith('nya') or word.endswith('kau') or word.endswith('lah') or word.endswith('kah'):
        word = word[:-3]
    elif word.lower().startswith('ter') or word.lower().startswith('kau'):
        word = word[3:]
    elif word.lower().startswith('se') or word.lower().startswith('ku') or word.lower().startswith('di'):
        word = word[2:]
    elif word.endswith('ku') or word.endswith('mu') or word.endswith('an') and not word.endswith('kan'):
        word = word[:-2]
    elif word.lower().endswith('-nya'):
        word = word[:-4]
    if word.endswith('kan'):
        word = {word[:-3]: 'v'}
    print('Word new ~ ' + str(word))
    return word


def take_inf(word):
    list_inf = word_inf(take_word_page(word))
    list_poss_checked = check_roots(list_inf, word)
    add_to_dict(list_poss_checked)
    return list_poss_checked


def if_list_checked(list_checked, word):
    dict_parts = {i[0][0]: i[1][0] for i in list_checked}
    if word.lower() in dict_parts.keys():
        part = dict_parts[word.lower()]
    elif word.capitalize() in dict_parts.keys():
        part = dict_parts[word.capitalize()]
    else:
        part = '?'
        print(word + ' ~ Нет в словаре')
    return part


def new_if_not(word):
    word1 = if_not_found(word)
    if type(word1) == list:
        # тут так вышло, что единственная возможность получить на выход список -
        # если корень на n или m после ME-
        part = 'v'
    elif type(word1) == dict:
        part = '|'.join(word1.values())
    else:
        if search_in_file(word1) is not None:
            print('Word ~ in dict')
            part = search_in_file(word1)
        else:
            list_poss_checked = take_inf(word1)
            part = if_list_checked(list_poss_checked, word1)
    return part


def main(text):
    down.check_file('DICTIONARY.txt')
    regex_word = re.compile('([a-zA-Z-]+)')
    text_1 = re.split(regex_word, text)
    text_new = []
    for i in range(len(text_1)):
        if re.search('\w', text_1[i]) is not None:
            word = text_1[i]
            print('Word ~ ' + word)
            if search_in_file(word) is not None:
                print('Word ~ in dict')
                part = search_in_file(word)
            else:
                print('Word ~ not in dict')
                list_poss_checked = take_inf(word)
                if list_poss_checked:
                    print('Word ~ in KBBI')
                    part = if_list_checked(list_poss_checked, word)
                    if part == '?':
                        part = new_if_not(word)
                else:
                    print('Word ~ not in KBBI')
                    part = new_if_not(word)
            line = word + '{' + part + '}'
            text_new.append(line)
        else:
            text_new.append(text_1[i])
    print(''.join(text_new))


# main(text_try)
# with open('sth1.json', 'r', encoding='utf-8') as f:
#     new_list_json = json.loads(f.read())
# LIST_JSON.update(new_list_json)
# with open('sth1.json', 'w', encoding='utf-8') as f:
#     json.dump(LIST_JSON, f, ensure_ascii=False, indent=4)
if __name__ == "__main__":
    print('')
