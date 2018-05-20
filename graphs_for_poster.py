import sqlite3
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


conn = sqlite3.connect(os.path.join('.', 'KorpusBD.sqlite'))
c = conn.cursor()


# c.execute('SELECT year FROM poems_all WHERE year != "---"')
# years = c.fetchall()
# years_clean = []
# for i in years:
#     pos_year = str(i[0])[-4:]
#     if '.' in pos_year:
#         new = str(pos_year).split('.')
#         y = new[-1]
#         while len(y) < 4:
#             y = y + '0'
#         print(pos_year + ' ~ ' + y)
#         pos_year = y
#     # year = str(i[0])[-4:]
#     years_clean.append(int(pos_year))
# # print(years_clean)
# print(years_clean)
#
# # years_gaps = ['1900-1910', '1911-1920', '1921-1930', '1931-1940', '1941-1950',
# #               '1951-1960', '1961-1970', '1971-1980', '1981-1990', '1991-2000',
# #               '2001-2010', '2011-2018']
# # years_gaps_dict = {}
# # for i in years_gaps:
# #     year_start = int(i.split('-')[0])
# #     year_end = int(i.split('-')[1])
# #     years_suit = []
# #     for n in years_clean:
# #         if n <= year_end and n >= year_start:
# #             years_suit.append(n)
# #     years_gaps_dict[i] = len(years_suit)
# # print(years_gaps_dict)
# # dict_years = {year: years_clean.count(year) for year in years_clean}
# # print(dict_years)
#
#
# def find_10s(year):
#     years_gaps = ['1900-1910', '1911-1920', '1921-1930', '1931-1940', '1941-1950',
#                   '1951-1960', '1961-1970', '1971-1980', '1981-1990', '1991-2000',
#                   '2001-2010', '2011-2018']
#     for i in years_gaps:
#         year_start = int(i.split('-')[0])
#         year_end = int(i.split('-')[1])
#         if year_start <= year <= year_end:
#             return i
#         # years_gaps_dict[i] = len(years_suit)
#
#
# # data = np.array([[i, years_gaps_dict[i]] for i in years_gaps_dict.keys()])
# data = np.array([[i, find_10s(i)] for i in years_clean])
# df = pd.DataFrame(data, columns=['year', '10s'])
# df = df.sort_values('10s')
# # print(df)
# # print('Данные для построения графика сформированы...')
# # ax = sns.pointplot("year", "count", data=df, color='g', size=6, aspect=2, legend_out=False)
# fig, ax = plt.subplots()
# sns.countplot(x="10s", data=df, ax=ax, palette='Reds')
# # ax.set_axis_labels("year_10s", "count")
# # ax.set_xticklabels(rotation=90)
# plt.setp(ax.get_xticklabels(), rotation=45)
# plt.xlabel('years')
# plt.ylabel('count')
# plt.tight_layout()
# plt.savefig('years_10.png', format='png')
#
# plt.show()
#

# plt.show()
# plt.savefig('years_all.png', format='png')
c.execute('SELECT place FROM poems_all WHERE place != "---"')
cities = c.fetchall()
cities_new = []
for i in cities:
    cities_new.append(i[0])
cities_new = [i for i in cities_new if cities_new.count(i) > 1]
data = np.array([[i, cities_new[i]] for i in range(len(cities_new))])
df = pd.DataFrame(data, columns=['index', 'city'])
# df = df.sort_values('10s')
fig1, ax1 = plt.subplots()
sns.countplot(x="city", data=df, ax=ax1, palette='Reds')
plt.setp(ax1.get_xticklabels(), rotation=90)
plt.xlabel('city')
plt.ylabel('count')
plt.tight_layout()
plt.savefig('cities.png', format='png')

plt.show()