import download_module as down
from bs4 import BeautifulSoup
import re
import sqlite3
import os
import traceback


# Краулер для сайта Мустофы Бисри
def gusmus_crouler():
    poems = []
    for n in range(1, 12):
        page = down.download('http://gusmus.net/puisi/?N={}'.format(str(n)))
        page1 = down.del_html(page)
        soup = BeautifulSoup(page1, 'lxml')
        container = soup.find_all('div', {'class': 'col-xs-12 col-sm-10 blog-content'})
        for i in container:
            regex = re.compile('<.*?>', re.DOTALL)
            text = re.sub(regex, '\n', str(i))
            text_ready = re.sub('\n{2,}', '\n', text)
            text_ready = re.sub('\xa0', ' ', text_ready)
            poems.append(text_ready.strip())
            file_name = 'Mustofa Bisri\\A. Mustofa Bisri - ' + text_ready.strip().split('\n')[0].capitalize() + '.txt'
            print(file_name)
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write('http://gusmus.net/puisi/?N={}'.format(str(n)))
                f.write(text_ready)
    print(poems)


# Собираем инфу со страниц
def poems_info(filename):
    print(filename)
    infa = {}
    with open(filename, 'r', encoding='utf-8') as f:
        all_text = f.readlines()
        infa['url'] = all_text[0].strip()
        infa['name'] = all_text[1].strip().capitalize()
        infa['author'] = 'A. Mustofa Bisri'
        infa['text'] = '\n'.join(all_text[3:]).strip()
        infa['year'] = '---'
    return infa


# Скачиваем страницу с поэзией Абдулы Хади (там оч хреновый сайт, много лишнего и расположено хз как, легче по
# отдельности нужное достать
def abdul_hadi_html():
    page = down.download('http://www.jendelasastra.com/dapur-sastra/dapur-jendela-sastra/lain-lain/puisi-puisi-abdul-hadi-wm')
    page1 = down.del_html(page)
    with open('abdul_h.html', 'w', encoding='utf-8') as f:
        f.write(page1)
    return page1


# Теги-теги-теги и БАЦ стихи
def abdul_hadi_poems():
    with open('abdul_h.html', 'r', encoding='utf-8') as f:
        html_text = f.read()
    soup = BeautifulSoup(html_text, 'lxml')
    container = soup.find('div', {'class': 'content'})
    texts = str(container)
    texts = re.sub('\xa0', '', texts)
    texts = re.sub('<strong>(\s)?</strong>', '', texts)
    texts_list = texts.split('<strong>')
    regex = re.compile('<.*?>', re.DOTALL)
    new_list = []
    for i in texts_list:
        a = re.sub(regex, '', i)
        if a != '\n':
            new_list.append(a)
    for i in new_list:
        filename = 'Abdul Hadi WM\\' + i.strip().split('\n')[0].capitalize().strip() + '.txt'
        filename = re.sub('[~#&%*{}:?"|+/<>]', '', filename)
        print(filename)
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(i)
            print('Ну вроде ок...')
        except Exception:
            with open('errors.log', 'a') as f:
                f.write('{}\n'.format(traceback.format_exc()))
            print('Ooops!')


# опять инфа (сколько ж можно с ней ф-й делать...)
def abdul_hadi_infa(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        all_text = f. read()
    all_lines = all_text.strip().split('\n')
    name = all_lines[0].capitalize()
    author = 'Abdul Hadi WM'
    url = 'http://www.jendelasastra.com/dapur-sastra/dapur-jendela-sastra/lain-lain/puisi-puisi-abdul-hadi-wm'
    if '19' in all_lines[-1]:
        year = all_lines[-1]
        text = '\n'.join(all_lines[1:-1]).strip()
    else:
        year = ''
        text = '\n'.join(all_lines[1:]).strip()
    return {'name': name, 'year': year, 'text': text, 'url': url, 'author': author}


# Вставляем в БД
def insert_into_bd(infa: dict):
    conn = sqlite3.connect(os.path.join('.', 'KorpusBD.sqlite'))
    c = conn.cursor()
    c.execute('SELECT poem_name FROM poems_info WHERE author = (?)', [infa['author']])
    existed = []
    for i in c.fetchall():
        existed.append(i[0].strip())
    if infa['name'].strip() not in existed:
        c.execute('INSERT OR IGNORE INTO poems_info (poem_name, poem_url, author, year) VALUES (?, ?, ?, ?)', [infa['name'], infa['url'], infa['author'], infa['year']])
        c.execute('INSERT OR IGNORE INTO poems (poem_text, poem_name) VALUES (?, ?)', [infa['text'], infa['name']])
        conn.commit()
        print('В базу данных внесены изменения')
    else:
        print(infa['name'] + ' - Такое стихотворение уже существует')


# ООО, мое любимое. Сайт haripuisi, тут стоооока всего.
# Скачиваем первую страницу архива
def haripuisi_html(url):
    page = down.download(url)
    page = down.del_html(page)
    with open('page.html', 'w', encoding='utf-8') as f:
        f.write(page)
    soup = BeautifulSoup(page, 'lxml')
    return soup


# Вылавливаем ВСЕ ссылки на стихи. Каеф, полноценный краулер, наконец-то!
def haripuisi_urls(url):
    print(url)
    soup = haripuisi_html(url)
    urls = []
    try:
        try_sth = soup.find('section', {'class': 'site-content'})
        for link in try_sth.find_all('a'):
            b = link.get('href')
            if (b not in urls) and ('/' in b):
                urls.append(b)
        print(urls)
        regex_urls_posts = re.compile('http://www.haripuisi.com/arsip/[0-9]+')
        url_poem = []
        for url in urls:
            if re.fullmatch(regex_urls_posts, url) is not None:
                url_poem.append(url)
        previous_post = try_sth.find('div', {'class': 'nav-previous'}).find('a').get('href')
        print(len(url_poem))
        return [url_poem, previous_post]
    except Exception:
        with open('errors.log', 'a') as f:
            f.write('{}\n'.format(traceback.format_exc()))
        print('It seems done ?_?')
        return [[], '']


# не смотрите на название, тут просто вызываются всякие полезные функции:))
def main(dirname):
    file_list = os.listdir(dirname)
    if dirname == 'Mustofa Bisri':
        for file_name in file_list:
            file_name = dirname + '\\' + file_name
            infa = poems_info(file_name)
            insert_into_bd(infa)
    elif dirname == 'Abdul Hadi WM':
        for file_name in file_list:
            file_name = dirname + '\\' + file_name
            infa = abdul_hadi_infa(file_name)
            insert_into_bd(infa)


main('Mustofa Bisri')
main('Abdul Hadi WM')


# ...и тут тоже
def main1():
    url = 'http://www.haripuisi.com/arsip/category/puisi'
    list_ = haripuisi_urls(url)
    while list_[1] != '':
        with open('urls.txt', 'a', encoding='utf-8') as f:
            for i in list_[0]:
                f.write(i+'\n')
        prev = list_[1]
        list_ = haripuisi_urls(prev)
    print('I hope it\'s really done, but to be on the safe side there is a file with error logs')


# чем переделывать предыдущую функцию, чтобы она ловила последнюю страницу, я лучше ее отдельно выловлю
def the_last_page():
    url = 'http://www.haripuisi.com/arsip/category/puisi/page/34'
    soup = haripuisi_html(url)
    urls = []
    try_sth = soup.find('section', {'class': 'site-content'})
    for link in try_sth.find_all('a'):
        b = link.get('href')
        if (b not in urls) and ('/' in b):
            urls.append(b)
    print(urls)
    regex_urls_posts = re.compile('http://www.haripuisi.com/arsip/[0-9]+')
    url_poem = []
    for url in urls:
        if re.fullmatch(regex_urls_posts, url) is not None:
            url_poem.append(url)
    with open('urls.txt', 'a', encoding='utf-8') as f:
        for i in url_poem:
            f.write(i + '\n')
    return url_poem


# ну ясно вроде из названия, да? Скачиваем, достаем, записываем в предварительные файлы
def haripuisi_download_poems(url):
    page_poem = down.download(url)
    page_poem = down.del_html(page_poem)
    soup = BeautifulSoup(page_poem, 'lxml')
    filename = re.sub('[~#&%*{}:?"|+/<>]', '', str(soup.title.string)).strip() + '.txt'
    get_poem = soup.find('div', {'class': 'entry-content'}).contents
    div_tag = re.compile('<div.*?>.*?</div>', re.DOTALL)
    poem = []
    for i in get_poem:
        poem_with_tags = re.sub(div_tag, '', str(i))
        poem1 = re.sub('<.*?>', '\n', poem_with_tags)
        poem.append(poem1)
    with open('haripuisi\\' + filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(poem))
    print(filename + ' - done')


# Добавляем к каждому стихотворению юрл - для коллекции, значица
def haripuisi_insert_url(url):
    page_poem = down.download(url)
    page_poem = down.del_html(page_poem)
    soup = BeautifulSoup(page_poem, 'lxml')
    filename = re.sub('[~#&%*{}:?"|+/<>]', '', str(soup.title.string)).strip() + '.txt'
    with open('haripuisi\\' + filename, 'a', encoding='utf-8') as f:
        f.write('\n' + url)
    print(filename + ' - done')


# ...ничего нового.
def main3():
    with open('urls.txt', 'r', encoding='utf-8') as f:
        urls = f.readlines()
    for url in urls:
        url = url.strip()
        try:
            haripuisi_insert_url(url)
        except Exception:
            with open('errors_crouler.log', 'a') as f:
                f.write(url + '\n')
                f.write('{}\n'.format(traceback.format_exc()))
            print('Упс! Что-то пошло не так... Ссылка с ошибкой записана в файл.')


# работаем с файлами, выпавшими в ошибку (у меня со второго круга нескачанным еще никто не уходил!)
def main_errors():
    with open('errors_crouler.log', 'r', encoding='utf-8') as f:
        text = f.read()
    regex = re.compile('http://www.haripuisi.com/arsip/[0-9]+')
    urls = re.findall(regex, text)
    for url in urls:
        url = url.strip()
        try:
            haripuisi_insert_url(url)
        except Exception:
            with open('errors_crouler1.log', 'a') as f:
                f.write(url + '\n')
                f.write('{}\n'.format(traceback.format_exc()))
            print('Упс! Что-то пошло не так... Ссылка с ошибкой записана в файл.')


# вид инфы, который получился после добавления ее в файлы, абсолютно неудобоварим для разметки.
# ту би он зе сейф сайд, мы все это перезальем в новые файлики в пафосной папочке haripuisi_clean с красивой разметочкой
def text_with_info(filename):
    with open('haripuisi\\' + filename, 'r', encoding='utf-8') as f:
        whole = f.read()
    whole = re.sub('\xa0', '', whole)
    parts = re.split('\n{2,}', whole)
    print(parts)
    infa1 = re.match('Puisi (.*?)Hari Puisi Indonesia', filename).group(1)
    author = infa1.split(' - ')[1].strip()
    name = infa1.split(' - ')[0].strip()
    if parts[0] == '':
        parts.remove(parts[0])
    i = 0
    while i < 2:
        if parts[0].strip() == author.strip() or parts[0].strip() == name.strip():
            parts.remove(parts[0])
        i += 1
    if parts[0].startswith(':'):
        parts.remove(parts[0])
    url = parts[-1]
    parts.remove(parts[-1])
    sumber = '---'
    year = '---'
    if re.search('[Ss]umber:', parts[-2]) is not None:
        sumber = re.sub('[Ss]umber:', '', parts[-2]).strip()
        parts.remove(parts[-2])
    elif re.search('[Ss]umber:', parts[-1]) is not None:
        sumber = re.sub('[Ss]umber:', '', parts[-1]).strip()
        parts.remove(parts[-1])
    if re.search('[0-9]{4}', parts[-1]) is not None:
        year = parts[-1]
        parts.remove(parts[-1])
    poem_text = '\n'.join(parts)
    with open('haripuisi_clean\\' + filename, 'w', encoding='utf-8') as f:
        f.write('Author: ' + author + '\n\nName: ' +
                name + '\n\nSumber: ' + sumber + '\n\nYear: ' +
                year + '\n\nURL: ' + url + '\n\nPoem text: \n' + poem_text)


# text_with_info('Puisi (Apa yang tak dapat kauhancurkan) - Sitor Situmorang (1923-2014) - Hari Puisi Indonesia.txt')


# хех
# больше error.log богу логов / лагов / багов (нужное подчеркнуть)
def main4():
    file_list = os.listdir('haripuisi')
    for file_name in file_list:
        print(file_name)
        try:
            text_with_info(file_name)
            print(file_name + ': DONE')
        except Exception:
            with open('errors_cleaning_mess.log', 'a') as k:
                k.write(file_name + '\n')
                k.write('{}\n'.format(traceback.format_exc()))
            print('Oops! Something\'s gone wrong. Check out this file!')


# main4()


# кое-где дата слепилась с местом, это нужно выловить. Плюс
# нужно удалить даты жизни авторов - ибо нафиг
def final_cleaning(file_name):
    with open('haripuisi_clean\\' + file_name, 'r', encoding='utf-8') as f:
        mess = f.read()
    mess_splited = mess.split('\n\n')
    mess_splited[0] = re.sub('\(.*?\)', '', mess_splited[0]).strip()
    # print(mess_splited)
    # if ',' in mess_splited[3].split(':')[1]:
    #     place_list = mess_splited[3].split(':')[1].split(', ')[:-1]
    #     place = ', '.join(place_list).strip()
    #     mess_splited[3] = re.sub(place + ', ', '', mess_splited[3])
    #     # print(place)
    #     mess_splited.insert(3, 'Place: ' + place.capitalize())
    for i in range(len(mess_splited)):
        if re.match('\(.*?\)', mess_splited[i].split(':')[1].strip()) is not None:
            mess_splited[i] = re.sub('[()]', '', mess_splited[i])
        mess_splited[i] = re.sub(' {2,}', ' ', mess_splited[i])
    # mess_splited[2] = re.sub('\n', ' ', mess_splited[2])
    text_new = '\n\n'.join(mess_splited)
    with open('haripuisi_clean\\' + file_name, 'w', encoding='utf-8') as k:
        k.write(text_new)


# нууу.... что-то новенькое... нет.
def main5():
    file_list = os.listdir('haripuisi_clean')
    for file_name in file_list:
        print(file_name)
        try:
            final_cleaning(file_name)
            print(file_name + ': DONE')
        except Exception:
            with open('errors_cleaning_mess1.log', 'a') as k:
                k.write(file_name + '\n')
                k.write('{}\n'.format(traceback.format_exc()))
            print('Oops! Something\'s gone wrong. Check out this file!')


# main5()


# здесь должна была быть ОЧЕНЬ ПАФОСНАЯ ФУНКЦИЯ, обрабатывающая "чистые" файлы и дочищающая их (ибо кое-где теги-таки
# поехали и Ресурс, например, уехал в Год, а Год, соответственно, прилип к тексту). Но нет, мне слишком влом ее писать.
# А 836 файлов вручную обработать не влом было, да...


# И кстати, не спрашивайте, почему вся разметка на английском, и только "Ресурс" на индонезийском. Пожалуйста, не надо.


# Что-то не так в датском королевстве. Пропал файл, нашедшему вознаграждение - вкусная конфетка:)
def sth():
    file_list1 = os.listdir('haripuisi')
    file_list2 = os.listdir('haripuisi_clean')

    result=list(set(file_list1) ^ set(file_list2))

    print(result)


# Ура, конфета заслужена! А файл не исчез, он просто был лишним на этом празднике жизни... Копией, то есть xD


# 21:46. Я так и не залила них...я в базу, но я пошла за конфеткой. Покедова. BRB


# 21:48. Заслуженная конфета съедена, молоко за вредность выпито (бедные мои глазки...), ГоТоВ к ТрУдУ и ОбОрОнЕ


# начнем, пожалуй, с авторов. (Прямо как вступление к докладу на конференцию прозвучало...)
# если конкретнее, нам надо проверить соответствие имеющихся и новых имен - может, другие сокращения, etc
def infa_haripuisi():
    conn = sqlite3.connect(os.path.join('.', 'KorpusBD.sqlite'))
    c = conn.cursor()
    c.execute('SELECT author FROM authors')
    author1 = [i[0] for i in c.fetchall()]
    files = os.listdir('haripuisi_clean')
    author2 = []
    infa = []
    for i in files:
        with open('haripuisi_clean\\'+i, 'r', encoding='utf-8') as f:
            whole = f.read()
        parts = whole.split('\n\n')
        dict = {part.split(':', maxsplit=1)[0].strip(): part.split(':', maxsplit=1)[1].strip() for part in parts}
        # ща буит мясо (и многа букафф)
        # А если серьезно, то это неприятно, но сделать надо:(
        if dict['Author'] == 'Acep Zamzam Noor':
            dict['Author'] = 'Acep Zam-zam Noor'
        elif dict['Author'] == 'Budiman S Hartoyo':
            dict['Author'] = 'Budiman S. Hartoyo'
        elif dict['Author'] == 'D Zawawi Imron':
            dict['Author'] = 'D. Zawawi Imron'
        elif dict['Author'] == 'Emha Ainun Nadjib':
            dict['Author'] = 'Emha Ainun Najib'
        elif dict['Author'] == 'Goenawan Mohamad':
            dict['Author'] = 'Goenawan Mohammad'
        elif dict['Author'] == 'Gol A Gong':
            dict['Author'] = 'Gola Gong'
        elif dict['Author'] == 'Gus tf':
            dict['Author'] = 'Gus tf Sakai'
        elif dict['Author'] == 'Korie Layun Rampan':
            dict['Author'] = 'Korrie Layun Rampan'
        elif dict['Author'] == 'Kurniawan Djunaedhi':
            dict['Author'] = 'Kurniawan Djunaedhie'
        elif dict['Author'] == 'Muhamad Yamin':
            dict['Author'] = 'Muhammad Yamin'
        elif dict['Author'] == 'Ramadhan KH':
            dict['Author'] = 'Ramadhan K.H.'
        elif dict['Author'] == 'Roestam Effendi':
            dict['Author'] = 'Rustam Effendi'
        elif dict['Author'] == 'Sutan Takdir Alisjahbana':
            dict['Author'] = 'Sutan Takdir Alisyahbana'
        elif dict['Author'] == 'Toto Sudarto Bachtiar':
            dict['Author'] = 'Toto Sudarto Bahtiar'
        elif dict['Author'] == 'Rendra':
            dict['Author'] = 'W.S. Rendra'
        elif dict['Author'] == 'A Muttaqin':
            dict['Author'] = 'A. Muttaqin'
        elif dict['Author'] == 'Ardy Cresna Crenata':
            dict['Author'] = 'Ardy Kresna Crenata'
        elif dict['Author'] == 'Arif Bagus Prasetyo':
            dict['Author'] = 'Arif B. Prasetyo'
        elif dict['Author'] == 'Dino F Umahuk':
            dict['Author'] = 'Dino F. Umahuk'
        elif dict['Author'] == 'Erich Langobelen':
            dict['Author'] = 'Erich Langgobelen'
        elif dict['Author'] == 'Jamal D Rahman':
            dict['Author'] = 'Jamal D. Rahman'
        elif dict['Author'] == 'Saini K.M.':
            dict['Author'] = 'Saini KM'
        elif dict['Author'] == 'Trisno Sumarjo':
            dict['Author'] = 'Trisno Sumardjo'
        elif dict['Author'] == 'Ulfatin Ch':
            dict['Author'] = 'Ulfatin Ch.'
        elif dict['Author'] == 'Mustofa Bisri':
            dict['Author'] = 'A. Mustofa Bisri'
        if dict['Author'] not in author2:
            author2.append(dict['Author'])

        infa.append(dict)
    author2.sort()
    # под комментами - не черновик, а просто те куски, которые нормально сработали во время многочисленных проверок
    # уже не под комментами, да
    with open('author1.txt', 'w', encoding='utf-8') as f:
        for i in author1:
            f.write(i[0] + '\n')
    with open('author2.txt', 'w', encoding='utf-8') as k:
        for i in author2:
            k.write(i + '\n')
    a = list(set(author2)-set(author1))
    for i in a:
        print(i)
        url = '---'
        c.execute('INSERT OR IGNORE INTO authors (author, url) VALUES (?, ?)', [i, url])
    for inf in infa:
        try:
            c.execute('SELECT poem_name FROM poems_info WHERE author = (?)', [inf['Author']])
            existed = []
            for i in c.fetchall():
                existed.append(i[0].strip())
            if inf['Name'].strip().capitalize() not in existed:
                c.execute('INSERT INTO poems_info (poem_name, poem_url, author, year) VALUES (?, ?, ?, ?)',
                          [inf['Name'].capitalize(), inf['URL'], inf['Author'], inf['Year']])
                c.execute('INSERT INTO poems (poem_text, poem_name) VALUES (?, ?)', [inf['Poem text'], inf['Name']])
                conn.commit()
            else:
                print(inf['Name'] + ' - Такое стихотворение уже существует')
        except Exception:
            print('Упс! ' + str(inf))


infa_haripuisi()
