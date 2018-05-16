import re
import download_module as down
from download_module import endswith_for_lists as good_end
from bs4 import BeautifulSoup as bs
import json
import os
import morph_nomor_TIGA as morph


CLITICS = ['lah', 'kah', 'nya', 'ku', 'mu', 'kau']


def take_word_page(word):
    html = down.download('https://kbbi.web.id/' + word.lower())
    if html is None:
        print('Прости, Настюш, но у тебя опять упал инет:(')
    else:
        with open(r'html_changing.txt', 'w', encoding='utf-8') as f:
            f.write(down.del_html(html.replace('&#183;', '')))
        return down.del_html(html.replace('&#183;', ''))


def reduplication_variants(word):
    def comparing(part1, part2, word=word):
        if part1 == part2:
            word = word.split('-')[0]
        elif re.search(part1, part2) is not None:
            word = part1
        elif re.search(part2, part1) is not None:
            if part1.startswith('me'):
                word = down.sandhi_men_pen(part1[2:])
            else:
                word = part2
        else:
            if part2.endswith('kan'):
                part2 = part2[:-3]
                comparing(part1, part2, word=word)
            elif part2.endswith('an'):
                part2 = part2[:-2]
                comparing(part1, part2, word=word)
            else:
                word = [part1, part2]
        return word
    # if '-' in word:
    part1 = word.lower().split('-')[0]
    part2 = word.lower().split('-')[1]
    return comparing(part1, part2, word)


def if_not_found(word):
    if word.endswith('nya') or word.endswith('kau') or word.endswith('lah') or word.endswith('kah'):
        word = word[:-3]
    elif word.lower().startswith('ter') or word.lower().startswith('kau') or word.lower().startswith('ber'):
        word = word[3:]
    elif word.lower().startswith('se') or word.lower().startswith('ku') or word.lower().startswith('di'):
        word = word[2:]
    elif word.endswith('ku') or word.endswith('mu') or word.endswith('an') and not word.endswith('kan'):
        word = word[:-2]
    elif (word.lower().startswith('me') is True and word.lower().startswith('memper') is False):
        word = down.sandhi_men_pen(word[2:])
    elif word.lower().endswith('-nya'):
        word = word[:-4]
    elif word.endswith('kan'):
        word = word[:-3]
    print('Word new ~ ' + str(word))
    return word


def word_inf(html):
    html = re.sub('<sup>.*?</sup>', '', html)
    soup = bs(html, 'lxml')
    container = soup.find('div', {'id': 'd1'})
    needed = str(container)
    a = re.findall('<b>(.*?)</b>', needed, re.DOTALL)
    return a


def changing_terms(new_list):
    if not new_list:
        return []
    word = [k.strip(' ') for k in new_list]
    word = [k for k in word if re.search('[^a-zA-Z-]', k) is None and re.search('\w', k) is not None]
    # слово может состоять ТОЛЬКО из букв и дефиса.
    word = [l for l in word if re.search('\d', l) is None and l != '']
    return word


def make_list_of_forms(word):
    words = word_inf(take_word_page(word))
    if not words:
        if '-' in word:
            word1 = reduplication_variants(word)
        else:
            word1 = if_not_found(word)
        if type(word1) == list:
            for i in word1:
                words.extend(word_inf(take_word_page(i)))
        else:
            words.extend(word_inf(take_word_page(word1)))
    elif '?' in words[0] and len(words) == 1:
        words = words[0].split('?')
        words = [i.strip() for i in words]
        words = [i.strip('1234567890,.:;!?-') for i in words]
        word = words[1]
        words.extend(word_inf(take_word_page(word)))
    if not word in words:
        words.append(word.lower())
    return words


def check_roots(words, word):
    if good_end(CLITICS, word)[0]:
        word = word[:-len(good_end(CLITICS, word)[1])]
    if not words:
        return []
    checked = []
    for n in words:
        if word.lower() in n.lower() or n.lower() in word.lower() or n[1:] in word:
            checked.append(n)
        else:
            if not (word.endswith('kan') or word.endswith('an')or word.endswith('ku') or word.endswith('nya') or word.endswith('mu') or word.endswith('kau')):
                for i in range(2, len(n)-1):
                    check_form = word[-i:]
                    if check_form in n:
                        checked.append(n)
                        break
            else:
                for i in range(1, len(n)-2):
                    check_form = word[:-i]
                    if check_form in n or check_form[1:] in n:
                        checked.append(n)
                        break
    return checked


def add_to_dict_json(list_same_root, list_js):
    some_new_list = []
    list_same_root = [i for i in list_same_root if len(i) > 1]
    a = len(list_same_root)
    for i in range(a):
        min_len = min([len(n) for n in list_same_root])
        for t in list_same_root:
            if len(t) == min_len:
                min_el = t
                some_new_list.append(min_el)
                list_same_root.remove(min_el)
                break
    list_same_root = some_new_list
    word_base = list_same_root[0]
    list_js[word_base] = list_same_root[1:]
    return


def main(text):
    down.check_file('WORDS_NEST.json')
    list_json = {}
    regex_word = re.compile('([a-zA-Z-]+)')
    text_1 = re.split(regex_word, text)
    with open('WORDS_NEST.json', 'r', encoding='utf-8') as k:
        json_str = k.read()
        if json_str != '':
            new_list_json = json.loads(json_str)
        else:
            new_list_json = {}
    for i in range(len(text_1)):
        if re.search('\w', text_1[i]) is not None:
            word = text_1[i]
            if '\"'+word+'\"' not in json_str and '\"'+word.lower()+'\"' not in json_str:
                words = make_list_of_forms(word)
                print(words)
                words = changing_terms(words)
                print(words)
                words = check_roots(words, word)
                print(words)
                if words:
                    print('Word ~ in KBBI')
                else:
                    # add_to_dict_json([word], list_json)
                    print('Word ~ not in KBBI')
                    word1 = if_not_found(word)
                    print('New word ~ ' + str(word1))
                    if type(word1) == list:
                        for i in word1:
                            words.extend(make_list_of_forms(i))
                    else:
                        words.extend(make_list_of_forms(word1))
                    print(words)
                    words = changing_terms(words)
                    print(words)
                    words = check_roots(words, word)
                    print(words)
                    if not words:
                        words.append(word)
                add_to_dict_json(words, list_json)
            else:
                print('Word ~ in json')
    list_json.update(new_list_json)
    with open('WORDS_NEST.json', 'w', encoding='utf-8') as f:
        json.dump(list_json, f, ensure_ascii=False, indent=4)
    return


if __name__ == "__main__":
    main('memberimu')