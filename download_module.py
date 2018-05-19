import urllib.request
import re
import sqlite3
import os


def download(pageUrl):
    try:
        page = urllib.request.urlopen(pageUrl)  # берем страницу
        html = page.read().decode('utf-8')  # достаем html
        print('Страница {} скачана.'.format(pageUrl))
        return html
    except:
        print('Error at ', pageUrl)
        return None


def del_html(html_text):
    import html
    html_text = html.unescape(html_text)
    return html_text



def check_file(file_name):
    if not os.path.exists(os.path.join('.',file_name)):
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write('')

# после BS эта хреновина достаточно бесполезна
def clean_html(html_text):
    regex_script = re.compile('<script.*?>.*?</script>', re.DOTALL)
    html_text = re.sub(regex_script, '', html_text)
    regex_style = re.compile('<style.*?>.*?</style>', re.DOTALL)
    html_text = re.sub(regex_style, '', html_text)
    regex_head = re.compile('<head>.*?</head>', re.DOTALL)
    html_text = re.sub(regex_head, '', html_text)
    regex_p = re.compile('</?p.*?>', re.DOTALL)
    html_text = re.sub(regex_p, '\n', html_text)
    html_text = re.sub('</?br( /)?>\n*', '\n', html_text)
    regex_tags_all = re.compile('<.*?>', re.DOTALL)
    html_text_wt = re.sub(regex_tags_all, '', html_text)
    html_text_wt = re.sub('\r', '', html_text_wt)
    html_text_clean = re.sub('\s{2,}', '\n', html_text_wt)
    html_text_clean = re.sub('\n+', '\n', html_text_clean)
    print(html_text_clean.split('\n'))

    # a = html_text_wt.split('\n')
    # html_text_list = []
    # for i in range(len(a)):
    #     if a[i] != '':
    #         html_text_list.append(a[i])
    # print(html_text_list)
    # html_text_clean = '\n'.join(html_text_list)
    return html_text_clean


def count_syllables(line):
    line_new = re.sub('(ai)|(au)|(oi)', 'γ', line)
    regex = re.compile('a|e|i|o|u|γ')
    syllables = len(re.findall(regex, line_new))
    return syllables


def take_alll():
    conn = sqlite3.connect(os.path.join('.', 'main_bd13_SOS_shit.sqlite'))
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
    return words


def count_lines(poem):
    poem_splited = poem.splitlines()
    return len(poem_splited)


def sandhi_men_pen(root):
    if root[1] in 'fvb':
        root_origin = root[1:]
    elif root[0:2] == 'ng':
        if root[2] == 'g' or root[2] == 'h' or root.startswith('ngkh'):
            root_origin = root[2:]
        else:
            root_origin = [root[2:], 'k' + root[2:], root]
    elif root[0] in 'lrwy':
        root_origin = root
    elif root[0] == 'n':
        if root[1] == 'y':
            root_origin = ['s' + root[2:], root]
        elif root[1] in 'cjdz' or root.startswith('nsy'):
            root_origin = root[1:]
        else:
            root_origin = [root, 't' + root[1:]]
    else:
        root_origin = [root, 'p' + root[1:]]
    return root_origin


# то же (word[2:])
def sandhi_ber_per(root):
    vowels = 'aeiou'
    if root.startswith('r'):
        if root[1] in vowels:
            root_origin = [root[1:], root]
        else:
            root_origin = root[1:]
    elif 'ajar' in root:
        if root.startswith('l'):
            root_origin = root[1:]
    # если после ber стоит CerC (где C - согласная, например kerja), r выпадает
    else:
        root_origin = root
    return root_origin


def startswith_for_lists(list_starts, str):
    new_list = []
    for i in list_starts:
        if str.startswith(i):
            new_list.append(i)
    if new_list:
        if len(new_list) > 1:
            el = max({len(i): i for i in new_list})
            return True, el
        elif len(new_list) == 1:
            el = new_list[0]
            return True, el
    else:
        el = ''
        return False, el
    return


def endswith_for_lists(list_starts, str):
    new_list = []
    for i in list_starts:
        if str.endswith(i):
            new_list.append(i)
    if new_list:
        if len(new_list) > 1:
            el = max({len(i): i for i in new_list})
            return True, el
        elif len(new_list) == 1:
            el = new_list[0]
            return True, el
    else:
        el = ''
        return False, el
    return


if __name__ == "__main__":
    print(count_words())

