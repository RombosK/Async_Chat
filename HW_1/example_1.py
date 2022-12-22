import subprocess
import locale

"""1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате
и проверить тип и содержание соответствующих переменных. Затем с помощью
онлайн-конвертера преобразовать строковые представление в формат Unicode и также
проверить тип и содержимое переменных."""

print('********** № 1 **********')
word_1 = 'разработка'
word_2 = 'сокет'
word_3 = 'декоратор'
print(type(word_1), type(word_2), type(word_3))
print((word_1, word_2, word_3))

word_1 = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
word_2 = '\u0441\u043e\u043a\u0435\u0442'
word_3 = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'
print(type(word_1), type(word_2), type(word_3))
print((word_1, word_2, word_3))

"""2. Каждое из слов «class», «function», «method» записать в байтовом типе
без преобразования в последовательность кодов (не используя методы encode
 и decode) и определить тип, содержимое и длину соответствующих переменных."""

print('********** № 2 **********')
word_1 = b'class'
word_2 = b'function'
word_3 = b'method'

print(type(word_1), type(word_2), type(word_3))
print(word_1, word_2, word_3)
print((len(word_1), len(word_2), len(word_3)))

"""3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в
байтовом типе"""

print('********** № 3 **********')
word_1 = b'attribute'
word_2 = 'класс'.encode('utf-8')  # невозможно записать в байтовом типе
word_3 = 'функция'.encode('utf-8')  # невозможно записать в байтовом типе
word_4 = b'type'

print((word_1, word_2, word_3, word_4))

"""4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из
строкового представления в байтовое и выполнить обратное преобразование (используя
методы encode и decode)."""

print('********** № 4 **********')
word_1 = 'разработка'.encode('utf-8')
word_2 = 'администрирование'.encode('utf-8')
word_3 = b'protocol'
word_4 = b'standard'

print((word_1, word_2, word_3, word_4))
word_1 = word_1.decode('utf-8')
word_2 = word_2.decode('utf-8')
word_3 = word_3.decode('utf-8')
word_4 = word_4.decode('utf-8')
print((word_1, word_2, word_3, word_4))

"""5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из
байтовового в строковый тип на кириллице."""

print('********** № 5 **********')
args_1 = ['ping', 'yandex.ru']
args_2 = ['ping', 'youtube.com']

subproc_ping = subprocess.Popen(args_1, stdout=subprocess.PIPE)
for line in subproc_ping.stdout:
    print(line.decode('cp866'), end='')

subproc_ping = subprocess.Popen(args_2, stdout=subprocess.PIPE)
for line in subproc_ping.stdout:
    print(line.decode('cp866'), end='')

"""6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое
программирование», «сокет», «декоратор». Проверить кодировку файла по умолчанию.
Принудительно открыть файл в формате Unicode и вывести его содержимое."""

print('********** № 6 **********')
print(locale.getpreferredencoding())

file = open('test_file.txt', 'w')
file.write("сетевое программирование\n")
file.write("сокет\n")
file.write("декоратор\n")
print(f'Кодировка файла по умолчанию - {file.encoding}')
file.close()

# with open('test_file.txt', encoding='utf-8') as file:
#     for line in file:
#         print(line, end='')
# UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf1 in position 0: invalid continuation byte
"""Установленa Windows"""
with open('test_file.txt', encoding='cp1251') as file:
    for line in file:
        print(line, end='')
