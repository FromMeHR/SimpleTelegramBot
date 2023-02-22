import requests
import random
import telebot
from bs4 import BeautifulSoup as b

API_Key = 'yourtoken'
URL = 'https://www.anekdot.ru/last/good/'
r = requests.get(URL)
def parser(url):
    soup = b(r.text, 'html.parser')  # весь код в html parser из библиотеки BeautifulSoup
    anekdots = soup.find_all('div', class_='text')  # print(anekdots) все теги содержимые с класcом div
    return [c.text for c in anekdots]
list_of_jokes = parser(URL)
random.shuffle(list_of_jokes) # перемешали анекдоты в списке

bot = telebot.TeleBot(API_Key)
@bot.message_handler(commands=['start1'])

def hello(message):
    bot.send_message(message.chat.id, "Hello! If you want to smile enter one number[1,9]: ")
@bot.message_handler(content_types=['text'])
def jokes(message):
    if message.text.lower() in '123456789':
        bot.send_message(message.chat.id, list_of_jokes[0])  # берём первый попавшийся элемент
        del list_of_jokes[0] # и удаляем его чтобы не повторялся
    else:
        bot.send_message(message.chat.id, "Enter number from range: ")
bot.polling()


