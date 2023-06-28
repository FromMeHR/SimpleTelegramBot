import requests
import random
import telebot
import pytz
from geopy.geocoders import Nominatim
from datetime import datetime
from timezonefinder import TimezoneFinder
from imdb import IMDb
from background import keep_alive
from bs4 import BeautifulSoup as bs
from translate import Translator
from telebot import types
from PIL import Image
from io import BytesIO

weather_api = "2a160c093921552181779f7152c68f35"
geolocator = Nominatim(user_agent="weather_bot")
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
def get_random_topical_movie_in_theaters():
    url = 'https://www.rottentomatoes.com/browse/movies_in_theaters/critics:certified_fresh~sort:popular'
    r = requests.get(url)
    html = bs(r.content, 'html.parser')
    movie_links = html.find_all('div', class_='js-tile-link')
    image_links = []
    movie_titles = []
    release_dates = []
    critics_scores = []
    movie_urls = []
    for link in movie_links:
        img_tag = link.find('img', class_='posterImage')
        src = img_tag['src']
        image_links.append(src)
        title_tag = link.find('span', {'class': 'p--small', 'data-qa': 'discovery-media-list-item-title'})
        movie_title = title_tag.get_text(strip=True)
        movie_titles.append(movie_title)
      
        date_tag = link.find('span', {'class': 'smaller', 'data-qa': 'discovery-media-list-item-start-date'})
        release_date = date_tag.get_text(strip=True).replace('Opened ', '')
        release_dates.append(release_date)
      
        score_tag = link.find('score-pairs')
        critics_score = score_tag['criticsscore']
        critics_scores.append(critics_score)
      
        url_tag = link.find('a', {'data-qa': 'discovery-media-list-item-caption'})
        movie_url = url_tag['href']
        movie_urls.append(movie_url)
    random_index = random.randint(0, len(movie_titles) - 1)
    random_image_link = image_links[random_index]
    random_movie_title = movie_titles[random_index]
    random_release_date = release_dates[random_index]
    random_critics_score = critics_scores[random_index]
    random_critics_score_percent = f"{random_critics_score}%"
    random_movie_url = movie_urls[random_index]
    full_movie_url = f"https://www.rottentomatoes.com{random_movie_url}"

    movie_info_response = requests.get(full_movie_url)
    movie_info_html = bs(movie_info_response.content, 'html.parser')
    genre_tag = movie_info_html.find('b', {'class': 'info-item-label', 'data-qa': 'movie-info-item-label'}, string='Genre:')
    if genre_tag:
        genre_value_tag = genre_tag.find_next_sibling('span', {'class': 'info-item-value', 'data-qa': 'movie-info-item-value'})
        if genre_value_tag:
            genre = " ".join(genre_value_tag.get_text(strip=True).split())
        else:
            genre = "N/A"
    else:
        genre = "N/A"
    return random_movie_title, random_release_date, random_image_link, random_critics_score_percent, genre
def get_current_time(city):
    geolocator = Nominatim(user_agent="my-app")
    location_of_city = geolocator.geocode(city)
    if location_of_city:
        tf = TimezoneFinder()
        latitude, longitude = location_of_city.latitude, location_of_city.longitude
        timezone = pytz.timezone(tf.timezone_at(lng=longitude, lat=latitude))
        current_time = datetime.now(timezone)
        return current_time.strftime("%B %d, %Y %H:%M:%S")
    else:
        return "N/A"

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
        "/weather - Get information about the current weather in a specific city",
        "/time_in_city - Get current time in a specific city",
        "/random - Generate a random number from 1 to 100",
        "/randommovieinfo - Get a random movie with its information",
        "/random_topical_movie_in_theaters - Get a random fresh movie in theaters from Rotten Tomatoes",
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
        bot.register_next_step_handler(message, process_number_input_joke)
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
@bot.message_handler(commands=['random_topical_movie_in_theaters'])
def random_topical_movie_in_theaters_command(message):
    movie_info = get_random_topical_movie_in_theaters()
    response = requests.get(movie_info[2])
    image = Image.open(BytesIO(response.content))
    new_size = (166, 250)
    image = image.resize(new_size)
    image_buffer = BytesIO()
    image.save(image_buffer, format='JPEG')
    image_buffer.seek(0)
    bot.send_photo(message.chat.id, image_buffer)
    response = "Title: " + movie_info[0] + "\nRelease Date (Theaters): " + str(movie_info[1]) + "\n"\
                "Critics' score: " + movie_info[3] + "\nGenres: " + movie_info[4]
    bot.send_message(message.chat.id, response)
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
    bot.send_poll(message.chat.id, poll_question, options)

time_in_city = {}
weather_city = {}
@bot.message_handler(commands=['time_in_city'])
def time_in_city_command(message):
    time_in_city[message.chat.id] = True
    weather_city[message.chat.id] = False  # сбрасываем weather_city
    bot.send_message(message.chat.id, "Enter the name of a city to get the current time: ")
@bot.message_handler(commands=["weather"])
def weather_command(message):
    weather_city[message.chat.id] = True
    time_in_city[message.chat.id] = False  # сбрасываем time_in_city
    bot.send_message(message.chat.id, "Enter the name of a city in order to get information about weather: ")
translator = Translator(from_lang='ru', to_lang='en')
@bot.message_handler(func=lambda message: time_in_city.get(message.chat.id, False))
def get_time_in_city(message):
    city = message.text
    translated_city = translator.translate(city)
    location_of_city = geolocator.geocode(translated_city)
    if location_of_city:
        current_time = get_current_time(translated_city)
        bot.send_message(message.chat.id, f"Current time in {translated_city}: {current_time}")
    else:
        bot.send_message(message.chat.id, "Wrong city name")
    time_in_city[message.chat.id] = False

@bot.message_handler(func=lambda message: weather_city.get(message.chat.id, False))
def get_weather_info(message):
    code_to_smile = {
        "Clear": "Clear ☀️",
        "Clouds": "Cloudy ☁️",
        "Drizzle": "Drizzle ☔",
        "Rain": "Rainy ☔",
        "Thunderstorm": "Thunderstorm ⚡",
        "Mist": "Mist 🌫️",
        "Snow": "Snow ❄️"
    }
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={weather_api}&units=metric"
        )
        data = r.json()
        city = data["name"]
        current_weather = data["main"]["temp"]
        weather_info = data["weather"][0]["main"]
        if weather_info in code_to_smile:
            wd = code_to_smile[weather_info]
        else:
            wd = "I can't determine the weather"
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        bot.reply_to(message, f"Weather in {city}:\nTemperature: {current_weather}°C {wd}\n"
                             f"Humidity: {humidity}%\nWind: {wind} m/s\n")

        weather_city[message.chat.id] = False
    except:
        bot.reply_to(message, "Wrong city name")
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
