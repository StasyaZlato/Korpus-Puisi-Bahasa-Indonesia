from flask import Flask
from flask import request, render_template, redirect, url_for
import re
import os
import sqlite3


app = Flask(__name__)

conn = sqlite3.connect(os.path.join('.', 'main_bd13_SOS_shit.sqlite'))
c = conn.cursor()
c.execute('''SELECT poems_info.id_poem, poems_info.poem_name, poem_url, author, year, poem_text
              FROM poems_info INNER JOIN poems ON poems_info.id_poem = poems.id_poem''')
infa = c.fetchall()

@app.route('/')
def index():
    try:
        with open('index.txt', 'r', encoding='utf-8') as f:
            nums_line = f.read()
        id = int(nums_line.split()[-1].strip())
    except Exception:
        id = 1
    infa1 = infa[id-1]
    dict_inf = {infa1[0]: infa1[1:6]}
    name = dict_inf[id][0].strip()
    url = dict_inf[id][1].strip()
    author = dict_inf[id][2].strip()
    year = dict_inf[id][3]
    if year == None:
        year = '---'
    text = dict_inf[id][4]
    text = '\n'.join([i.strip() for i in text.split('\n') if i != ''])
    if request.args:
        keys = ['id', 'name', 'url', 'author', 'year',
                'place', 'text', 'num_lines', 'num_syl',
                'rhyme', 'form', 'refren', 'figure_poetry', 'source', 'other']
        conn = sqlite3.connect(os.path.join('.', 'main_bd13_SOS_shit.sqlite'))
        c = conn.cursor()
        c.execute('''INSERT INTO poems_all 
        (id_poem, 
        poem_name, 
        poem_url,
        author,
        year,
        place,
        poem_text,
        num_lines,
        num_syl,
        rhyme,
        form,
        repetition,
        figure_poetry,
        source,
        other_marks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  [request.args[i] for i in keys])

        conn.commit()
        # with open('check_pleaase.txt', 'a', ) as f:
        #     for i in keys:
        #         f.write(i + ': ' + str(request.args[i]) + '\t')
        with open('index.txt', 'a', encoding='utf-8') as k:
            k.write(str(id + 1) + ' ')
        return redirect(url_for('next'))
    return render_template('form.html', id = id, name = name, url = url, author = author,
                           year = year, text = text, wise_words = 'Ты сможешь, солнце!',
                           rows = str(len(text.splitlines())))


@app.route('/next')
def next():
    return render_template('next.html')


if __name__ == '__main__':
    app.run(debug=True)