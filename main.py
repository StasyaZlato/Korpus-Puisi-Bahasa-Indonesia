import try_sth_new as TSN
import download_module as down
import parts
import morph_nomor_TIGA as morph


TEXT_TRY = '''Pandanglah kota dan matahari, simpang dan tiang-tiang ini
Di mana pernah melintas bayanganmu
Pernah sekejap kita di sini
Mengiringkan waktu
Tiada sesuatu yang pasti.  Berbahagialah menyusur jalan
Resah dari tempat demi tempat
Dan aku hanya bisa memberimu secercah ciuman
Yang hanya kita bisa nikmat
Semoga sesudah kota dan matahari, simpang dan tiang-tiang ini
Engkau pun bisa bertetap hati
pada segala yang akan datang
Selamat jalan, anak sayang!'''

TEXT_TRY = 'kulit'

# !!!ta' --> tak --> tidak
# anda может быть приклеено к слову!
parts.main(TEXT_TRY)
TSN.main(TEXT_TRY)
print(morph.main(TEXT_TRY))
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


