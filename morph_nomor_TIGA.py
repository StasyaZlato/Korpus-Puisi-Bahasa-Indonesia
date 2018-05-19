import re
import json
from download_module import startswith_for_lists as good_start, endswith_for_lists as good_end
from pprint import pprint
import time
start_time = time.time()

CLITICS = ['lah', 'kah', 'nya', 'ku', 'mu', 'kau']
CLITICS_PRE = ['ku', 'kau', 'di']
SUFFIXES = ['', 'kan', 'an', 'nya', 'ku', 'mu', 'kau',
            'i', 'lah', 'kah']
PREFIXES = ['', 'ber', 'meN', 'peN', 'per', 'ter',
            'se', 'ke', 'di', 'kau', 'ku', 'N', 'pe']


def take_text(text):
    regex_word = re.compile('(\w+-?\w*)')
    words_list = re.split(regex_word, text)
    return words_list


def take_dict():
    with open('WORDS_NEST.json', 'r', encoding='utf-8') as f:
        dict_strr = f.read()
    dict_dictt = json.loads(dict_strr)
    return dict_strr, dict_dictt


def find_in_dict_new(word, dict_strr, dict_dictt: dict):
    word_base = word
    root = ''
    clitic = ''
    red = False
    morph = word
    if not '\"' + word + '\"' in dict_strr and not '\"' + word.lower() + '\"' in dict_strr:
        print('Слово не в списках')
        if good_end(CLITICS, word)[0]:
            clitic = '-' + good_end(CLITICS, word)[1]
            word = word[:-len(good_end(CLITICS, word)[1])]
            print('Слово кончается на клитику')
        elif good_start(CLITICS_PRE, word)[0]:
            print('Слово начинается на клитику')
            clitic = good_start(CLITICS_PRE, word)[1] + '-'
            word = word[len(good_start(CLITICS_PRE, word)[1]):]
        elif '-' in word:
            red = True
            if '\"' + word.split('-')[0] + '\"' in dict_strr or '\"' + word.split('-')[0].lower() in dict_strr:
                word = word.split('-')[0]
            else:
                word = word.split('-')[1]
        else:
            return [word, word, word]
    for k, v in dict_dictt.items():
        if k == word or k == word.lower():
            if red:
                root = k
                # morph = complex_both(word_base, root)
                morph = reduplication(word_base, root)
            else:
                root = k
                morph = root
            break
        elif v != {}:
            if word in v or word.lower() in v:
                root = k
                if '-' in word:
                    morph = reduplication(word_base, root)
                else:
                    morph = complex_both(word_base, root)
                break
        else:
            morph = word
    if clitic.startswith('-'):
        return [word_base, root, morph + clitic]
    else:
        return [word_base, root, clitic + morph]


def sandhi_generator_men(root, first_letter='m'):
    if root[0] in 'bvf':
        form = first_letter + 'em' + root
    elif root[0] in 'dcj' or root.startswith('sy'):
        form = first_letter + 'en' + root
    elif root[0] == 't':
        form = first_letter + 'en' + root[1:]
    elif root[0] == 'p':
        form = first_letter + 'em' + root[1:]
    elif root[0] == 's' and root[1] != 'y':
        form = first_letter + 'eny' + root[1:]
    elif root[0] == 'k' and root[1] != 'h':
        form = first_letter + 'eng' + root[1:]
    elif root[0] == 'g' or root[0] == 'h':
        form = first_letter + 'eng' + root
    elif root[0] == 'kh':
        form = first_letter + 'eng' + root
    elif root[0] in 'lrmnyw' or root.startswith('ng'):
        form = first_letter + 'e' + root
    else:
        form = first_letter + 'eng' + root
    return form


def complex_both(word, root):
    prefixes = PREFIXES
    suffixes = SUFFIXES
    possible_forms = []
    combs = list(set([(i, k) for i in prefixes for k in prefixes]))
    combs1 = list(set([(i,k) for i in suffixes for k in suffixes]))
    combs = [(combs[i][0], combs[i][1]) for i in range(len(combs)) if combs[i][0] != combs[i][1] and (word.startswith(combs[i][0]) or word.startswith(combs[i][0][:2]) or combs[i][0] == 'N')]
    combs1 = [(combs1[i][0], combs1[i][1]) for i in range(len(combs1)) if combs1[i][0] != combs1[i][1] and word.endswith(combs1[i][1])]
    for n in combs:
        for t in combs1:
            if n == ('meN', 'ber'):
                form = generator_suf(generator_suf(generator_pref(root, 'memper'), t[0]), t[1])
            else:
                form = generator_suf(generator_suf(generator_pref(generator_pref(root, n[1]), n[0]), t[0]), t[1])
            if form == word or form == word.lower():
                list_ = [n[0], n[1], root, t[0], t[1]]
                list_ = [i for i in list_ if i != '']
                if 'N' in list_:
                    possible_forms.append(list_)
                else:
                    return '-'.join(list_)
    if possible_forms == []:
        return word
    for i in possible_forms:
        if len(i) > 1:
            if not(i[1] == 'N' or (i[0] == 'N' and i[1] in prefixes)):
                return '-'.join(i)
    return possible_forms[0]


def sandhi_generator_ber(root, first_letter='b'):
    if root.startswith('r'):
        form = first_letter + 'e' + root
    elif re.match('[^aeiouAEIOU]er[^aeiouAEIOU]', root) is not None:
        form = first_letter + 'e' + root
    elif root.endswith('r'):
        form = first_letter + 'e' + root + '|' + first_letter + 'er' + root
    else:
        form = first_letter + 'er' + root
    return form


def generator_suf(root, fix):
    return root + fix


def generator_pref(root, pref):
    if pref == 'meN' or pref == 'peN':
        return sandhi_generator_men(root, first_letter=pref[0])
    elif pref in ['ber', 'per', 'ter']:
        return sandhi_generator_ber(root, first_letter=pref[0])
    elif pref == 'N':
        return sandhi_generator_men(root)[2:]
    else:
        return pref + root


def reduplication(word, root):
    word_parts = word.split('-')
    word_part1, word_part2 = word_parts[0], word_parts[1]
    a = complex_both(word_part1, root)
    b = complex_both(word_part2, root)
    if a is not None and b is not None:
        return a + '-' + b
    return word


def main(text):
    list_w = take_text(text)
    new_text = []
    dict_str, dict_dict = take_dict()
    print('Словари взяты.')
    for i in list_w:
        if re.search('\w', i) is not None:
            print(i)
            a = find_in_dict_new(i, dict_str, dict_dict)
            print('Поиск осуществлен.')
            if a != None:
                new_text.append({'слово': a[0], 'корень': a[1], 'форма': a[2]})
                print('Слово добавлено в список')
            else:
                new_text.append(i)
        else:
            new_text.append(i)
    return new_text


if __name__ == "__main__":
    print(main(text='Saya mau pertunjukan'))
    print("--- %s seconds ---" % (time.time() - start_time))

