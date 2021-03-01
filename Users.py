import sqlite3
import telebot
from lxml.html import fromstring
import urllib.request
import schedule
from threading import Thread

conn = sqlite3.connect(r'users.db', check_same_thread=False)
cur = conn.cursor()

bot = telebot.TeleBot("1568343871:AAEtV0lRpYJomkdSY8WPQFdH6Jmtt-ePbmA")

def mailing():
    subers = list(cur.execute("SELECT * FROM `subers` WHERE status=1").fetchall())
    for s in subers:
        response = urllib.request.urlopen('https://www.rbc.ru/crypto/currency/btcusd').read()
        page = fromstring(response)
        course = page.xpath('/html/body/div[4]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[1]/div[2]')
        rate = page.xpath('/html/body/div[4]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[1]/div/div[1]/div[2]/span')
        info = {
            "name": 'Bitcoin',
            "course": course[0].text.replace(' ',''),
            "rate": rate[0].text.replace(' ',''),
        }
        message = info["name"] + '\n' + info["course"] + info["rate"]
        bot.send_message(s[3], message)

cur.execute("""CREATE TABLE IF NOT EXISTS subers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname TEXT,
    lastname TEXT,
    user_id TEXT, 
    status INT);""")
conn.commit()

def adder(id_of_user, firstname, lastname):
    user_id = id_of_user
    status = 1
    cur.execute(f"INSERT INTO subers(firstname, lastname ,user_id, status) VALUES('{firstname}', '{lastname}', '{user_id}', '{status}');")
    conn.commit()

def updater(id_of_user):
    user_id = id_of_user
    status = 1
    cur.execute(f"UPDATE subers set status = {status} WHERE user_id = {user_id}")
    conn.commit()

@bot.message_handler(commands=['add'])
def add(message):
    result = str(cur.execute(f"SELECT * FROM subers WHERE user_id = {message.from_user.id}").fetchall())
    result = result.replace('[]','')
    if result == '':
        adder(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
    else:
        updater(message.from_user.id)
    bot.send_message(message.chat.id, "Вы успешно подписались на рассылку.")
    

@bot.message_handler(commands=['unadd'])
def unadd(message):
    user_id = message.from_user.id
    status = 0
    cur.execute(f"UPDATE subers set status = {status} WHERE user_id = {user_id}")
    conn.commit()
    bot.send_message(message.chat.id, "Вы успешно отписались от рассылки.")

schedule.every(10).seconds.do(mailing)

def pending():
    while True:
        schedule.run_pending()
    
th = Thread(target=pending)
while True:
    th.start()
    bot.polling(none_stop=True)
