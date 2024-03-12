import telebot
import openai
import pytesseract
from PIL import Image
import io

# OpenAI API key
openai.api_key = "ENTER-KEY-HERE"
messages = [ {"role": "system", "content": "You are a intelligent assistant."} ]

# Replace ‘YOUR_API_TOKEN’ with the API token you received from the BotFather
API_TOKEN = "YOUR_API_TOKEN"
bot = telebot.TeleBot(API_TOKEN)

homework_list = ["HW1","HW2","HW3","HW4","HW5"]
command_list = ["/help - see list of commands", "/timetable - view timetable", "/hw - view homework list", "/addhw - add item to your homework list", "removehw - remove specified item from your homework list", "/gpt - talk with ChatGPT", "/hwhelp - ask ChatGPT for homework help by sending a photo of your question"]
user_states = {}

# help command
@bot.message_handler(commands=["help"])
def sendImage(message):
    user_id = message.from_user.id
    bot.reply_to(message, "\n".join(command_list))

# timetable
@bot.message_handler(commands=["timetable"])
def sendImage(message):
    user_id = message.from_user.id
    photo = open('/Users/tedgoh/Downloads/timetable303.png', 'rb')
    bot.send_photo(user_id, photo)

# view homework
@bot.message_handler(commands=["hw"])
def sendHomework(message):
    bot.reply_to(message, "\n".join(homework_list))

# add homework
@bot.message_handler(commands=['addhw'])
def add_homework(message):
    # Set the user state to 'waiting0'
    user_states[message.chat.id] = 'waiting0'
    bot.reply_to(message, "What would you like to add?")
    
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'waiting0')
def receive_homework(message):
    # Add the homework to the list
    homework_list.append(message.text)
    # Reset the user state
    user_states[message.chat.id] = None
    bot.reply_to(message, "Homework added successfully.")

# remove homework
@bot.message_handler(commands=['removehw'])
def remove_homework(message):
    # Set the user state to 'waiting1'
    user_states[message.chat.id] = 'waiting1'
    bot.reply_to(message, "What would you like to remove?")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'waiting1')
def unreceive_homework(message):
    # Add the homework to the list
    homework_list.remove(message.text)
    # Reset the user state
    user_states[message.chat.id] = None
    bot.reply_to(message, "Homework removed.")

# askGPT
@bot.message_handler(commands=['gpt'])
def contactGPT(message):
    # Set the user state to 'contactGPT'
    user_states[message.chat.id] = 'contactGPT'
    bot.reply_to(message, "Enter prompt: ")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'contactGPT')
def unreceive_homework(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Please wait a moment.")
    # GPT Prompt
    messages.append({"role": "user", "content": message.text})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    # Reset the user state
    user_states[message.chat.id] = None
    bot.reply_to(message, response.choices[0].message.content)
    messages.append({"role": "assistant", "content": response.choices[0].message.content})

# homeworkhelp
@bot.message_handler(commands=['hwhelp'])
def contact(message):
    # Set the user state to 'hwhelp'
    user_states[message.chat.id] = 'hwhelp'
    bot.reply_to(message, "Send a photo of your question.")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'hwhelp', content_types=['photo'])
def tesseract(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Please wait a moment.")
    # get text from image
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    image_stream = io.BytesIO(downloaded_file)
    image = Image.open(image_stream)
    text = pytesseract.image_to_string(image)
    # GPT Prompt
    messages.append({"role": "user", "content": text})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    # Reset the user state
    user_states[message.chat.id] = None
    bot.reply_to(message, response.choices[0].message.content)
    messages.append({"role": "assistant", "content": response.choices[0].message.content})

# start the bot
bot.infinity_polling()