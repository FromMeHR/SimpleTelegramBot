import requests
import random
import telebot
from background import keep_alive
from bs4 import BeautifulSoup as bs
from translate import Translator
from telebot import types
from PIL import Image
from io import BytesIO

API_Key = 'your api'
URL = 'https://www.anekdot.ru/last/good/'
r = requests.get(URL)
def parser(url):
    r = requests.get(url)
    soup = bs(r.text, 'html.parser')
    anekdots = soup.find_all('div', class_='text')
    return [c.text for c in anekdots]
def process_number_input_joke(message):
    try:
        number = int(message.text)
        if 1 <= number <= 9:
            joke = list_of_jokes.pop(0)
            bot.send_message(message.chat.id, joke)
        else:
            bot.send_message(message.chat.id, "Invalid number. Enter a number from 1 to 9.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid input. Enter a number from 1 to 9.")
def process_number_input_movie(message):
    try:
        number = int(message.text)
        if 1 <= number <= 10:
            movie_info = top10_movies_info[number - 1]
            if movie_info[3]:
                response = requests.get(movie_info[3])
                image = Image.open(BytesIO(response.content))
                new_size = (166, 250)
                image = image.resize(new_size)
                image_buffer = BytesIO()
                image.save(image_buffer, format='JPEG')
                image_buffer.seek(0)
                bot.send_photo(message.chat.id, image_buffer)
            else:
                bot.send_message(message.chat.id, "Movie poster's not available.")
            bot.send_message(message.chat.id, "Title: " + movie_info[0])
            bot.send_message(message.chat.id, "Year: " + str(movie_info[1]))
            bot.send_message(message.chat.id, "Rating: " + str(movie_info[5]))

            if isinstance(movie_info[4], list):
                country = ', '.join(movie_info[4])
            else:
                country = str(movie_info[4])
            bot.send_message(message.chat.id, "Country: " + country)
            bot.send_message(message.chat.id, "Genres: " + movie_info[2])
        else:
            bot.send_message(message.chat.id, "Invalid number. Enter a number from 1 to 10.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid input. Enter a number from 1 to 10.")
def get_random_movie_info():
    url = 'https://randomfilm.ru/'
    r = requests.get(url)
    html = bs(r.content, 'html.parser')

    title = html.find('h2').text.strip()
    image_tag = html.find('img', src=lambda x: 'images' in x)
    image_url = image_tag['src']
    full_path = "https://randomfilm.ru/" + image_url
    soup = bs(r.content, 'html.parser')
    film_info = soup.find('div', align='center')
    table_rows = film_info.find_all('tr')
    year = None
    country = None
    genre = None
    for row in table_rows:
        columns = row.find_all('td')
        for column in columns:
            if 'Год' in column.text:
                year = column.text.split(':')[1].strip()
            elif 'Страна' in column.text:
                country = column.text.split(':')[1].strip()
            elif 'Жанр' in column.text:
                genre = column.text.split(':')[1].strip()
    translator = Translator(from_lang='ru', to_lang='en')
    if country:
        translated_country = translator.translate(country)
        if translated_country == ".":
            translated_country = "No info"
    if genre:
        translated_genre = translator.translate(genre)

    return title, full_path, year, translated_country, translated_genre
def get_top10_movies_info():
    movies = imdb.get_top250_movies()[:10]
    movie_info_list = []
    for movie in movies:
        imdb.update(movie)
        title = movie.get('title', 'Unknown')
        year = movie.get('year', 'Unknown')
        country = movie.get('country', 'Unknown')
        genres = ', '.join(movie.get('genres', []))
        cover_url = movie.get('cover url')
        rating = movie.get('rating', 'Unknown')
        movie_info_list.append((title, year, genres, cover_url, country, rating))

    return movie_info_list
def get_random_topical_movie_info():
    url = 'https://www.imdb.com/chart/moviemeter/?ref_=tt_ov_pop'
    r = requests.get(url)
    html = bs(r.content, 'html.parser')

    table = html.find('tbody', class_='lister-list')
    movies = table.find_all('tr')
    random_index = random.randint(0, len(movies) - 1)
    random_movie = movies[random_index]
    title_column = random_movie.find('td', class_='titleColumn')
    poster_column = random_movie.find('td', class_='posterColumn')
    rating_column = random_movie.find('td', class_='ratingColumn imdbRating')
    title = title_column.a.text.strip()
    translator = Translator(from_lang='uk', to_lang='en')
    title = translator.translate(title)

    poster_url = poster_column.find('img')['src']
    year = title_column.find('span', class_='secondaryInfo').text.strip('()')
    rank = poster_column.find('span', {'name': 'rk'})['data-value']
    rating = rating_column.strong.text.strip() if rating_column.strong else 'N/A'
    return title, year, poster_url, rating, rank

imdb = IMDb()
list_of_jokes = parser(URL)
random.shuffle(list_of_jokes)

bot = telebot.TeleBot(API_Key)
@bot.message_handler(func=lambda message: message.text.lower() == '/start')
def hello(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id, f"Hi, {user_name}!\nTo familiarize yourself with the functionality, enter the command /help!")
@bot.message_handler(commands=['help'])
def help_command(message):
    commands = [
        "/start - Start the bot",
        "/help - Show available commands",
        "/anecdote - Get a random anecdote",
        "/random - Generate a random number from 1 to 100",
        "/randommovieinfo - Get a random movie with its information",
        "/randomtopicalmovieimdb - Get a random current popular movie from IMDb",
        "/top10moviesimdb - Get information about one movie from IMDb's Top 10 Movies (wait half a minute)",
        "/vote - Create a poll \"What is your favorite movie?\"",
        "/play_tanks - Tanks: battle game 1vs1"
    ]
    bot.send_message(message.chat.id, "Available commands:\n" + "\n".join(commands))
@bot.message_handler(commands=['anecdote'])
def anecdote_command(message):
    if len(list_of_jokes) > 0:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, selective=True)
        numbers = [str(i) for i in range(1, 10)]
        markup.add(*numbers)
        bot.send_message(message.chat.id, "Enter a number from 1 to 9:", reply_markup=markup)
        bot.register_next_step_handler(message, process_number_input)
    else:
        bot.send_message(message.chat.id, "No more anecdotes available. Enter /help for available commands.")
@bot.message_handler(commands=['top10moviesimdb'])
def top10_movies_imdb_command(message):
    global top10_movies_info
    top10_movies_info = get_top10_movies_info()

    if len(top10_movies_info) > 0:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, selective=True)
        numbers = [str(i) for i in range(1, 11)]
        markup.add(*numbers)
        bot.send_message(message.chat.id, "Enter a number from 1 to 10:", reply_markup=markup)
        bot.register_next_step_handler(message, process_number_input_movie)
    else:
        bot.send_message(message.chat.id, "No movies available. Enter /help for available commands.")
@bot.message_handler(commands=['randomtopicalmovieimdb'])
def random_topical_movie_imdb_command(message):
    movie_info = get_random_topical_movie_info()
    if movie_info[2]:
        response = requests.get(movie_info[2])
        image = Image.open(BytesIO(response.content))
        new_size = (100, 160)
        image = image.resize(new_size)
        image_buffer = BytesIO()
        image.save(image_buffer, format='JPEG')
        image_buffer.seek(0)
        bot.send_photo(message.chat.id, image_buffer)
    else:
        bot.send_message(message.chat.id, "Movie poster's not available.")
    bot.send_message(message.chat.id, "Title: " + movie_info[0])
    bot.send_message(message.chat.id, "Year: " + str(movie_info[1]))
    bot.send_message(message.chat.id, "Rating: " + movie_info[3])
    bot.send_message(message.chat.id, "Current popularity rank: " + movie_info[4])
@bot.message_handler(commands=['random'])
def random_command(message):
    random_number = random.randint(1, 100)
    bot.send_message(message.chat.id, f"Random number: {random_number}")
@bot.message_handler(commands=['randommovieinfo'])
def random_movie_info_command(message):
    title, image_url, year, country, genre = get_random_movie_info()
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    new_size = (166, 250)
    image = image.resize(new_size)
    image_buffer = BytesIO()
    image.save(image_buffer, format='JPEG')
    image_buffer.seek(0)
    response = f"Title: {title}\n"
    bot.send_photo(message.chat.id, image_buffer)
    response += f"Year: {year}\n"
    response += f"Country: {country}\n"
    response += f"Genres: {genre}\n"
    bot.send_message(message.chat.id, response)
@bot.message_handler(commands=['vote'])
def poll_command(message):
    poll_question = "What is your favorite movie?"
    poll_options = ['The Shawshank Redemption (1994)', 'The Godfather (1972)', 'The Dark Knight (2008)', 'Schindler\'s List (1993)']
    options = [telebot.types.PollOption(option, "Option{}".format(index + 1)) for index, option in enumerate(poll_options)]
    poll = bot.send_poll(message.chat.id, poll_question, options)
class Tank:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp
        self.initial_hp = hp
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
    def is_alive(self):
        return self.hp > 0
    def reset_health(self):
        self.hp = self.initial_hp
available_tanks = {
    "ИС-2": Tank("ИС-2", 800),
    "Т-34": Tank("Т-34", 600),
    "КВ-2": Tank("КВ-2", 650)
}

enemy_tank = Tank("PzKpfw VI Tiger I", 800)
player_tank = None

@bot.message_handler(commands=['play_tanks'])
def start_game(message):
    global player_tank, enemy_tank
    player_tank = None
    enemy_tank.reset_health()
    for tank in available_tanks.values():
        tank.reset_health()
    bot.send_message(message.chat.id, "Welcome to the Tank Battle game!")
    bot.send_message(message.chat.id, "Available tanks:")
    for tank_name, tank in available_tanks.items():
        bot.send_message(message.chat.id, "- {} ({} HP)".format(tank_name, tank.hp))
    bot.send_message(message.chat.id, "Use /select_tank <tank_name> to choose your tank.")
@bot.message_handler(commands=['select_tank'])
def select_tank_command(message):
    global player_tank
    if player_tank is not None:
        bot.send_message(message.chat.id, "You have already selected a tank.")
        return
    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, "Please specify a tank name. Use /select_tank <tank_name>.")
        return
    tank_name = message.text.split(' ', 1)[1]
    if tank_name not in available_tanks:
        bot.send_message(message.chat.id, "Invalid tank name. Please choose from the available tanks.")
        return
    player_tank = available_tanks[tank_name]
    bot.send_message(message.chat.id, "You have selected the {} tank. The battle has just began!".format(tank_name))
    bot.send_message(message.chat.id, "Your tank: {} ({} HP)".format(player_tank.name, player_tank.hp))
    bot.send_message(message.chat.id, "Enemy tank: {} ({} HP)".format(enemy_tank.name, enemy_tank.hp))
    bot.send_message(message.chat.id, "The enemy came out from the corner, you can /shoot!")
@bot.message_handler(commands=['shoot'])
def shoot_command(message):
    global player_tank, enemy_tank
    if player_tank is None or not player_tank.is_alive() or not enemy_tank.is_alive():
        bot.send_message(message.chat.id, "The game is over. Use /play_tanks to play again.")
        return
    else:
        bot.send_message(message.chat.id, "The game is not over. Press /shoot faster!")
    player_damage = random.randint(150, 200)
    player_damage_2nd_possibility = random.randint(0, 3)
    enemy_damage = random.randint(150, 200)
    enemy_damage_2nd_possibility = random.randint(0, 3)

    if player_damage_2nd_possibility == 0:
        bot.send_message(message.chat.id, "Your shot ricocheted off the enemy tank. No damage made.")
    else:
        enemy_tank.take_damage(player_damage)
        enemy_hp = enemy_tank.hp
        bot.send_message(message.chat.id, "You made {} damage to the enemy tank. Enemy tank: ({} HP)".format(player_damage, enemy_hp))
    if enemy_damage_2nd_possibility == 0:
        bot.send_message(message.chat.id, "The enemy shot ricocheted off your tank. No damage taken.")
    else:
        player_tank.take_damage(enemy_damage)
        player_hp = player_tank.hp
        bot.send_message(message.chat.id, "The enemy tank made {} damage to your tank. Your tank: ({} HP)".format(enemy_damage, player_hp))
    if not player_tank.is_alive() and not enemy_tank.is_alive():
        bot.send_message(message.chat.id, "Both tanks have been destroyed! It's a draw.")
    elif not player_tank.is_alive():
        bot.send_message(message.chat.id, "Your tank {} has been destroyed. You lost the battle!".format(player_tank.name))
    elif not enemy_tank.is_alive():
        bot.send_message(message.chat.id, "Congratulations! You destroyed the enemy tank {}. You won the battle!".format(enemy_tank.name))
@bot.message_handler(content_types=['text'])
def handle_message(message):
    bot.send_message(message.chat.id, "Invalid command. Use /help to see available commands.")

keep_alive()
bot.polling(none_stop=True)
