import requests
import telebot
from telebot import types
import time
import json

bot = telebot.TeleBot('7060286846:AAEeodWAegv3834hYLeNN_wsHjpFDWpxfY4')  # Replace with your actual bot token

# Owner ID (replace with your actual owner ID)
owner_id = 1192484969 

# User Database (replace with your actual database structure)
users = {}

# Ban List
banned_users = []

# Spam List
spam_users = {} 

# Function to add a user to the spam list with a cooldown
def add_to_spam_list(user_id):
    spam_users[user_id] = int(time.time())
    save_spam_list()

# Function to check if a user is on cooldown
def is_on_cooldown(user_id):
    if user_id in spam_users:
        cooldown_time = 15  # Default cooldown time in seconds
        if user_id == owner_id:
            cooldown_time = 0  # Owner has no cooldown
        elif time.time() - spam_users[user_id] < cooldown_time:
            return True
    return False

# Function to save the spam list to a file
def save_spam_list():
    try:
        with open('spam.txt', 'w') as file:
            for user_id, timestamp in spam_users.items():
                file.write(f"{user_id},{timestamp}\n")
    except Exception as e:
        send_error_to_owner(e)

# Function to load the spam list from a file
def load_spam_list():
    try:
        with open('spam.txt', 'r') as file:
            for line in file:
                user_id, timestamp = line.strip().split(',')
                spam_users[int(user_id)] = int(timestamp)
    except FileNotFoundError:
        pass  # File doesn't exist, ignore
    except Exception as e:
        send_error_to_owner(e)

# Function to save the ban list to a file
def save_ban_list():
    try:
        with open('ban.txt', 'w') as file:
            for user_id in banned_users:
                file.write(f"{user_id}\n")
    except Exception as e:
        send_error_to_owner(e)

# Function to load the ban list from a file
def load_ban_list():
    try:
        with open('ban.txt', 'r') as file:
            for line in file:
                banned_users.append(int(line.strip()))
    except FileNotFoundError:
        pass  # File doesn't exist, ignore
    except Exception as e:
        send_error_to_owner(e)

# Function to save the user database to a file
def save_user_database():
    try:
        with open('database.txt', 'w') as file:
            for user_id, user_data in users.items():
                file.write(f"{user_id},{user_data['rank']},{user_data['username']}\n")
    except Exception as e:
        send_error_to_owner(e)

# Function to load the user database from a file
def load_user_database():
    try:
        with open('database.txt', 'r') as file:
            for line in file:
                user_id, rank, username = line.strip().split(',')
                users[int(user_id)] = {'rank': rank, 'username': username}
    except FileNotFoundError:
        pass  # File doesn't exist, ignore
    except Exception as e:
        send_error_to_owner(e)

# Function to send error messages to the bot owner
def send_error_to_owner(error):
    try:
        bot.send_message(owner_id, f"Error occurred: {error}")
    except Exception:
        pass  # Ignore any errors while sending the error message

# Load data from files when the bot starts
load_user_database()
load_ban_list()
load_spam_list()

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in users:
        bot.send_message(message.chat.id, 'Welcome back! 👋\nI can check the gate of a website.')
    else:
        bot.send_message(message.chat.id, 'Please register first using the /register command.')

# /register command (replace with your actual registration logic)
@bot.message_handler(commands=['register'])
def register(message):
    user_id = message.from_user.id
    if user_id not in users:
        # Add user to the database (replace with your database logic)
        users[user_id] = {'rank': 'Free User', 'username': None}
        bot.send_message(message.chat.id, 'You have successfully registered! You can now use the /url command.')
        add_to_spam_list(user_id)  # Add to spam list on registration
        save_user_database()  # Save the updated user database
    else:
        bot.send_message(message.chat.id, 'You are already registered.')

# /owner command
@bot.message_handler(commands=['owner'])
def owner(message):
    user_id = message.from_user.id
    if user_id == owner_id:
        bot.send_message(message.chat.id, 'You are the owner.')
    else:
        bot.send_message(message.chat.id, 'You are not authorized.')

# /ban command (replace with your actual banning logic)
@bot.message_handler(commands=['ban'])
def ban(message):
    user_id = message.from_user.id
    if user_id == owner_id:
        try:
            ban_id = int(message.text.split()[1])
            banned_users.append(ban_id)
            bot.send_message(message.chat.id, f'User with ID {ban_id} has been banned.')
            save_ban_list()  # Save the updated ban list
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, 'Please provide a valid user ID to ban.')
    else:
        bot.send_message(message.chat.id, 'You are not authorized.')

# /url command
@bot.message_handler(commands=['url'])
def url(message):
    user_id = message.from_user.id
    if user_id in users: # Check if user is registered
        if user_id in banned_users:
            bot.send_message(message.chat.id, 'You are banned from using this service.')
            return

        if is_on_cooldown(user_id):
            remaining_time = int(spam_users[user_id] + 5 - time.time())
            bot.send_message(message.chat.id, f'Please wait {remaining_time} seconds before using the command again.')
            return

        process_url_command(message)
    else:
        bot.send_message(message.chat.id, 'Please register first using the /register command.')

def process_url_command(message):
    user_id = message.from_user.id
    urls = message.text.split()[1:]
    if urls:
        bot.send_message(message.chat.id, 'Please wait, I\'m checking your URLs.')  

        for url in urls:
            response = requests.get(f'http://107.173.62.148:8080/?url={url}')
            if response.status_code == 200:
                data = json.loads(response.text)  # Parse the response as JSON
                result = f'✿ Website » {data.get("site", "N/A")}\n\n'
                result += f'✿ Captcha » {data.get("captcha", "N/A")}\n\n'
                result += f'✿ Cloudflare » {data.get("cloudflare", "N/A")}\n\n'
                result += f'✿ Gate » {", ".join(data.get("gate", []))}\n\n'  # Handle empty lists
                result += f'Checked by - ID: {user_id}, Name: {message.from_user.first_name} {message.from_user.last_name}\n\n'  # Remove rank 
                result += 'Owner - @xRonak' 

                bot.send_message(message.chat.id, result)
            else:
                bot.send_message(message.chat.id, f'Error fetching data for: {url}')
    else:
        bot.send_message(message.chat.id, 'Please use the command in the following format: /url http:// website_url')

    # Add the user to the spam list
    add_to_spam_list(user_id)

# /broadcast command
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    user_id = message.from_user.id
    if user_id == owner_id:
        try:
            # Send the message to all users
            for user_id in users:
                bot.send_message(user_id, message.text[len('/broadcast '):])
            bot.send_message(message.chat.id, 'Message broadcasted successfully.')
        except Exception as e:
            bot.send_message(message.chat.id, f'Error broadcasting: {e}')
    else:
        bot.send_message(message.chat.id, 'You are not authorized.')

#  /users command
@bot.message_handler(commands=['users'])
def users_list(message):
    user_id = message.from_user.id
    if user_id == owner_id:
        user_list = "\n".join(f"User ID: {user_id}" for user_id in users)
        bot.send_message(message.chat.id, f"Total users: {len(users)}\n\n{user_list}")
    else:
        bot.send_message(message.chat.id, 'You are not authorized.')

#  Default handler for other commands (ignore them)
@bot.message_handler(func=lambda message: True)
def default_handler(message):
    user_id = message.from_user.id
    if user_id not in users:
        bot.send_message(message.chat.id, 'Please register first using the /register command.')

#  Run the bot
bot.polling(none_stop=True)