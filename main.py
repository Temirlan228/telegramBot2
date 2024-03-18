import sqlite3
import telebot
import random
from telebot import types

connection = sqlite3.connect('question_answer_and_testname.db')
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS tests
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  test TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS questions
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  test_id INTEGER,
                  question TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS answers
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  question_id INTEGER,
                  answer TEXT)''')
connection.close()

bot = telebot.TeleBot('7137842657:AAEN9WRmVAT1J5qQw5RMzEjkoGAD7d83vfs')
chat_id = None



@bot.message_handler(commands=['Create_test'])
def create_test(message):
    test_name = bot.reply_to(message, 'Напишите название вашего теста')
    bot.register_next_step_handler(test_name, save_test_name)

def save_test_name(test_name):
    test_name_text = test_name.text
    print(test_name_text)
    connection = sqlite3.connect('question_answer_and_testname.db')
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO tests (test) VALUES (?)''', (test_name_text,))
    connection.commit()
    connection.close()
    create_question(test_name)

def create_question(message):
    question = bot.reply_to(message, 'Создайте свой вопрос')
    bot.register_next_step_handler(question, save_question)


def save_question(question):
    question_text = question.text
    connection = sqlite3.connect('question_answer_and_testname.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT MAX(id) FROM tests''')
    last_test_id = cursor.fetchone()[0]
    cursor.execute('''INSERT INTO questions (test_id, question) VALUES (?, ?)''', (last_test_id, question_text))
    connection.commit()
    connection.close()
    create_answer(question)


def create_answer(question):
    answer = bot.reply_to(question, 'Создайте свой ответ')
    bot.register_next_step_handler(answer, save_answer)


def save_answer(answer):
    answer_text = answer.text
    connection = sqlite3.connect('question_answer_and_testname.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT MAX(id) FROM questions''')
    last_question_id = cursor.fetchone()[0]
    cursor.execute('''INSERT INTO answers (question_id, answer) VALUES (?, ?)''', (last_question_id, answer_text))
    connection.commit()
    connection.close()
    bot.send_message(answer.chat.id, 'Хотите создать еще один ответ? (да/нет)')
    bot.register_next_step_handler(answer, process_response_answer)


def process_response_answer(message):
    response = message.text.lower()
    if response == 'да':
        create_answer(message)
    elif response == 'нет':
        bot.send_message(message.chat.id, 'Хотите создать еще один вопрос? (да/нет)')
        bot.register_next_step_handler(message, process_response_question)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, ответьте "да" или "нет".')
        bot.register_next_step_handler(message, process_response_answer)


def process_response_question(message):
    response = message.text.lower()
    if response == 'да':
        create_question(message)
    elif response == 'нет':
        bot.send_message(message.chat.id, 'Спасибо за создание тестов!')
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, ответьте "да" или "нет".')
        bot.register_next_step_handler(message, process_response_question)


@bot.message_handler(commands=['show_test'])
def show_test(message):
    global chat_id
    chat_id = message.chat.id
    conn = sqlite3.connect('question_answer_and_testname.db')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM tests''')
    tests = cur.fetchall()
    if tests:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [types.InlineKeyboardButton(f"{test[1]}",
        callback_data=f"Пришел ответ от show_test${test[0]}") for test in tests]
        keyboard.add(*buttons)
        bot.send_message(chat_id=chat_id, text="Тесты", reply_markup=keyboard)
    else:
        bot.send_message(chat_id=chat_id, text="нет тестов в базе данных")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data.split('$')
    who_send = data[0]
    if who_send == "Пришел ответ от show_test":
        finde_first_question(str(data[1]))
    if who_send == "Пришел ответ от random_answer":
        check_ans(data[1], data[2])

def finde_first_question(test_id):
    conn = sqlite3.connect('question_answer_and_testname.db')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM questions''')
    questions = cur.fetchall()

    if questions:
        for question in questions:
            if str(test_id) == str(question[1]):
                show_answer(question[0])
                break
def find_next_question(new_question_id, test_id):
    global chat_id
    check = False
    conn = sqlite3.connect('question_answer_and_testname.db')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM questions''')
    questions = cur.fetchall()
    for question in questions:
        if str(new_question_id) == str(question[0]) and str(test_id) == str(question[1]):
            check = True
            break
    if check == True:
        show_answer(new_question_id)
    if check == False:
        bot.send_message(chat_id=chat_id, text="Тест завершен")

def show_answer(question_id):
    conn = sqlite3.connect('question_answer_and_testname.db')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM answers''')
    answers = cur.fetchall()
    list_answer = []
    if answers:
        for answer in answers:
            if str(question_id) == str(answer[1]):
                list_answer.append(answer[2])
        return random_answer(list_answer, question_id)
    else:
        print("В базе данных нет вопросов.")
    conn.close()


def random_answer(list_answer, question_id):
    question_text = " "
    conn = sqlite3.connect('question_answer_and_testname.db')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM questions''')
    questions = cur.fetchall()
    if questions:
        for question in questions:
            if str(question_id) == str(question[0]):
                question_text = question[2]
                break
    global chat_id
    random.shuffle(list_answer)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [types.InlineKeyboardButton(f"{answer}",
    callback_data=f"Пришел ответ от random_answer${question_id}${answer}") for answer in list_answer]
    keyboard.add(*buttons)
    bot.send_message(chat_id=chat_id, text=question_text, reply_markup=keyboard)
    return True

def check_ans(question_id, ans):
    new_question_id = 0
    test_id = 0
    conn = sqlite3.connect('question_answer_and_testname.db')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM answers''')
    answers = cur.fetchall()
    conn.close()
    for answer in answers:
        if str(question_id) == str(answer[1]):
            str1 = str(answer[2])
            str2 = str(ans)
            if str1 == str2:
                bot.send_message(chat_id=chat_id, text="Правильно!")
                new_question_id = answer[1] + 1
                break
            else:
                bot.send_message(chat_id=chat_id, text=f"Не правильно!. Правильный ответ {answer[2]}")
                new_question_id = answer[1] + 1
                break
    conn = sqlite3.connect('question_answer_and_testname.db')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM answers''')
    questions = cur.fetchall()
    for question in questions:
        if str(question[0]) == str(question_id):
            test_id = question[1]
    find_next_question(new_question_id, test_id)
    conn.close()



bot.polling(none_stop=True)
