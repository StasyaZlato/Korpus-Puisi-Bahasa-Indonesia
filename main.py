import try_sth_new as TSN
import download_module as down
import parts
import morph_nomor_TIGA as morph
import sqlite3
import json
import re
import traceback
import time
start_time = time.time()



# TEXT_TRY = '''Pandanglah kota dan matahari, simpang dan tiang-tiang ini
# Di mana pernah melintas bayanganmu
# Pernah sekejap kita di sini
# Mengiringkan waktu
# Tiada sesuatu yang pasti.  Berbahagialah menyusur jalan
# Resah dari tempat demi tempat
# Dan aku hanya bisa memberimu secercah ciuman
# Yang hanya kita bisa nikmat
# Semoga sesudah kota dan matahari, simpang dan tiang-tiang ini
# Engkau pun bisa bertetap hati
# pada segala yang akan datang
# Selamat jalan, anak sayang!'''
#
# TEXT_TRY = 'kulit'

# !!!ta' --> tak --> tidak
# anda может быть приклеено к слову!
# parts.main(TEXT_TRY)


# TEXT_TRY = try_sth[0][8]
# list_parts = parts.main(TEXT_TRY)
# TSN.main(TEXT_TRY)
# list_morph = morph.main(TEXT_TRY)
# nda (ibunda)
# bahgia, bah’gia --> bahagia
# list_ = morph.main(TEXT_TRY)
# new_list = []
# for i in list_:
#     if type(i) == dict:
#         new_list.append(i['форма'])
#     else:
#         new_list.append(i)
# print(''.join(new_list))


def making_meta(list_bd, index):
    file_name = str(index) + '.json'
    author = list_bd[4]
    title = list_bd[2]
    genre = list_bd[12]
    if genre == '---':
        genre = 'стихотворение'
    year = list_bd[5]
    num_lines = down.count_lines(list_bd[8])
    rhyme = list_bd[11]
    id_bd = list_bd[1]
    syllables = [down.count_syllables(i) for i in list_bd[8].splitlines()]
    strofy = [len(i.splitlines()) for i in re.split('[{}]', list_bd[8]) if len(i.splitlines()) != 0]
    return {"file_name": file_name,
            "id_bd": id_bd,
            "author": author,
            "title": title,
            "genre": genre,
            "year": year,
            "num_lines": num_lines,
            "rhyme": rhyme,
            "syllables": syllables,
            "strofy": strofy}


# print(making_meta(try_sth[0]))


def making_poems(list_bd, index):
    text_poems = list_bd[8]
    strofy = [i for i in re.split('[{}]', text_poems) if i != '']
    strf = []
    for i in strofy:
        num_lines = len(i.splitlines())
        lines = []
        for line in i.splitlines():
            glosses = make_gloss(line)
            lines.append({'line': line, 'words': glosses, 'syllables': down.count_syllables(line)})
        strf.append({'strof': i, 'lines': lines, 'num_lines': down.count_lines(i)})
    return {'text': text_poems, 'strof': strf}


def make_gloss(line):
    # regex_word = re.compile('(\w+-?\w*)')
    # words_list = re.split(regex_word, line)
    parts_list = parts.main(line)
    TSN.main(line)
    morphp = morph.main(line)
    print(str(len(morphp)) + ' ' + str(len(parts_list)))
    print(morphp)
    line_list = []
    for i in range(len(parts_list)):
        if type(parts_list[i]) == dict:
            wf = parts_list[i]['токен']
            part = parts_list[i]['помета']
            if type(morphp[i]) == dict:
                lex = morphp[i]['корень']
                form = morphp[i]['форма']
                word = {'wf': wf,'wtype': 'word', 'ana': {'root': lex, 'pos': part, 'form': form}}
            else:
                word = {'wf': wf, 'wtype': 'punct'}
            line_list.append(word)
    return line_list


def make_json(list_bd, index):
    json_str = {'meta': making_meta(list_bd, index), "poem": making_poems(list_bd, index)}
    with open('json\\{}.json'.format(str(index)), 'w', encoding='utf-8') as f:
        json.dump(json_str, f, ensure_ascii=False, indent=4)
    return json_str


# print(make_json())
def main():
    conn = sqlite3.connect('KorpusBD.sqlite')
    c = conn.cursor()
    c.execute('SELECT * FROM poems_all WHERE id_poem >= 821 and id_poem < 900')
    try_sth = c.fetchall()
    index = 821
    for line_bd in try_sth:
        print('file №{}'.format(str(index)))
        try:
            make_json(line_bd, index)
        except Exception:
            with open('errors_json.log', 'a', encoding='utf-8') as f:
                f.write('{}{}{}\n'.format(str(index)+'\n', str(time.time()) + '\n', traceback.format_exc()))
        # make_json(line_bd, index)
        index += 1

main()
print("--- %s seconds ---" % (time.time() - start_time))

