import random

from dotenv import load_dotenv
import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton


load_dotenv()


API_TOKEN = os.getenv()


bot = telebot.TeleBot(API_TOKEN)


GUESS_NUMBER_GAME = 'Guess Number'
THE_FIELD_OF_WONDERS = 'The Field of Wonders'
TICK_TACK_TOE = 'Tick Tack Toe'


MainMenuKeyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

button_1 = KeyboardButton(GUESS_NUMBER_GAME)
button_2 = KeyboardButton(THE_FIELD_OF_WONDERS)
button_3 = KeyboardButton(TICK_TACK_TOE)


MainMenuKeyboard.add(button_1, button_2, button_3)


GUESS_NUMBER_PLAYERS = {}
GUESS_NUMBER_CONFIG = {
    "max_tries": 7,
    "min_number": 1,
    "max_number": 100,
}

TICK_TACK_TOE_PLAYERS = {}


@bot.message_handler(commands=['start'])
def start(message: Message):
    sent_message = bot.send_message(
        message.chat.id,
        "Welcome! Pick a game you'd like to play.",
        reply_markup=MainMenuKeyboard,
    )

    bot.register_next_step_handler(sent_message, handle_game_startup)


def handle_game_startup(message: Message):
    if message.text == GUESS_NUMBER_GAME:
        start_user_number_guess(message.chat.id)
    elif message.text == TICK_TACK_TOE:
        start_tick_tack_toe(message.chat.id)
    elif message.text == THE_FIELD_OF_WONDERS:
        start_the_field_of_wonders(message.chat.id)
    else:
        sent_message = bot.send_message(
            message.chat.id,
            "Welcome! Pick a game you'd like to play.",
            reply_markup=MainMenuKeyboard,
        )
        bot.register_next_step_handler(sent_message, handle_game_startup)


# - - -
# Number Guess Game
# - - -


def start_user_number_guess(chat_id: int):
    random_number = random.randint(
        GUESS_NUMBER_CONFIG["min_number"],
        GUESS_NUMBER_CONFIG["max_number"] + 1
    )

    GUESS_NUMBER_PLAYERS[chat_id] = {
        "number": random_number,
        "tries": 0,
    }

    reply = f"I'm thinking of a number between {GUESS_NUMBER_CONFIG["min_number"]} and {GUESS_NUMBER_CONFIG["max_number"]}. Write your guess:"
    sent_message = bot.send_message(chat_id, reply)
    bot.register_next_step_handler(sent_message, handle_user_number_guess)


def handle_user_number_guess(message: Message):
    user_guess = message.text
    chat_id = message.chat.id

    number_status = None

    if not user_guess.isdigit():
        sent_message = bot.send_message(chat_id, "Not a valid number. Try again!")
        bot.register_next_step_handler(sent_message, handle_user_number_guess)
        return

    user_guess = int(user_guess)
    if user_guess == GUESS_NUMBER_PLAYERS[chat_id]["number"]:
        del GUESS_NUMBER_PLAYERS[chat_id]

        bot.send_message(chat_id, "You win!")
        sent_message = bot.send_message(chat_id, "Welcome! Pick a game you'd like to play.", reply_markup=MainMenuKeyboard)
        bot.register_next_step_handler(sent_message, handle_game_startup)
        return

    elif user_guess < GUESS_NUMBER_PLAYERS[chat_id]["number"]:
        GUESS_NUMBER_PLAYERS[chat_id]["tries"] += 1
        number_status = "lower"
    
    else:
        GUESS_NUMBER_PLAYERS[chat_id]["tries"] += 1
        number_status = "bigger"

    if GUESS_NUMBER_PLAYERS[chat_id]["tries"] >= GUESS_NUMBER_CONFIG["max_tries"]:
        bot.send_message(chat_id, f"You lost! I guessed {GUESS_NUMBER_PLAYERS[chat_id]["number"]}")
        sent_message = bot.send_message(chat_id, "Welcome! Pick a game you'd like to play.", reply_markup=MainMenuKeyboard)
        bot.register_next_step_handler(sent_message, handle_game_startup)
        return

    sent_message = bot.send_message(chat_id, f"You're number is {number_status} than mine! Write your guess:")
    bot.register_next_step_handler(sent_message, handle_user_number_guess)


# - - -
# Tick Tack Toe
# - - -


def start_tick_tack_toe(chat_id: int):
    ...


def start_the_field_of_wonders(chat_id: int):
    ...


bot.infinity_polling()
