import os
import random

from dotenv import load_dotenv
import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton

from tick_tack_toe import (
    check_field_match,
    generate_keyboard_markup,
    make_bot_move,
    make_winner_text,
    update_field_sign,
)


load_dotenv()


API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")


bot = telebot.TeleBot(API_TOKEN)


GUESS_NUMBER_GAME = 'Guess Number'
TICK_TACK_TOE = 'Tick Tack Toe'


EASY_DIFFICULTY = "EASY"
NORMAL_DIFFICULTY = "NORMAL"
HARD_DIFFICULTY = "HARD"


MainMenuKeyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

button_1 = KeyboardButton(GUESS_NUMBER_GAME)
button_3 = KeyboardButton(TICK_TACK_TOE)
MainMenuKeyboard.add(button_1, button_3)


TickTackToeDifficultyKeyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

button_4 = KeyboardButton(EASY_DIFFICULTY)
button_5 = KeyboardButton(NORMAL_DIFFICULTY)
button_6 = KeyboardButton(HARD_DIFFICULTY)
TickTackToeDifficultyKeyboard.add(button_4, button_5, button_6)


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
        "Welcome! Pick a game you'd like to play. Enter /start to start from the beginning",
        reply_markup=MainMenuKeyboard,
    )

    bot.register_next_step_handler(sent_message, handle_game_startup)


def handle_game_startup(message: Message):
    if message.text == GUESS_NUMBER_GAME:
        start_user_number_guess(message.chat.id)
    elif message.text == TICK_TACK_TOE:
        start_tick_tack_toe(message.chat.id)
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
        GUESS_NUMBER_CONFIG["max_number"],
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
    TICK_TACK_TOE_PLAYERS[chat_id] = {
        "field": [["", "", ""], ["", "", ""], ["", "", ""],],
        "difficulty": None,
    }
    TICK_TACK_TOE_PLAYERS[chat_id]["player_sign"] = "X"
    TICK_TACK_TOE_PLAYERS[chat_id]["bot_sign"] = "O"

    sent_message = bot.send_message(chat_id, "Pick difficulty:", reply_markup=TickTackToeDifficultyKeyboard)
    bot.register_next_step_handler(sent_message, handle_difficulty_pick)


def handle_difficulty_pick(message: Message):
    if message.text not in [EASY_DIFFICULTY, NORMAL_DIFFICULTY, HARD_DIFFICULTY]:
        sent_message = bot.send_message(message.chat.id, "Invalid input! Pick difficulty:", reply_markup=TickTackToeDifficultyKeyboard)
        bot.register_next_step_handler(sent_message, handle_difficulty_pick)
        return

    # user always have first move
    TICK_TACK_TOE_PLAYERS[message.chat.id]["difficulty"] = message.text
    sent_message = bot.send_message(message.chat.id, "Your turn", reply_markup=generate_keyboard_markup(TICK_TACK_TOE_PLAYERS[message.chat.id]["field"]))
    bot.register_next_step_handler(sent_message, handle_tick_tack_toe)


def handle_tick_tack_toe(message: Message):
    chat_id = message.chat.id
    message_text = message.text

    # Validate message text
    if not len(message_text) == 3 or not message_text[1].isdigit():
        sent_message = bot.send_message(chat_id, "Invalid input", reply_markup=generate_keyboard_markup(TICK_TACK_TOE_PLAYERS[message.chat.id]["field"]))
        bot.register_next_step_handler(sent_message, handle_tick_tack_toe)
        return

    sign_position = int(message_text[1])
    
    # Update field according to user input
    TICK_TACK_TOE_PLAYERS[chat_id]["field"] = update_field_sign(
        TICK_TACK_TOE_PLAYERS[chat_id]["field"],
        TICK_TACK_TOE_PLAYERS[chat_id]["player_sign"],
        sign_position,
    )

    if check_field_match(TICK_TACK_TOE_PLAYERS[chat_id]["field"]):
        game_end_text = make_winner_text(TICK_TACK_TOE_PLAYERS[chat_id])
        sent_message = bot.send_message(chat_id, game_end_text, reply_markup=MainMenuKeyboard)
        bot.register_next_step_handler(sent_message, handle_game_startup)
        return
    
    bot.send_message(chat_id, "Bot is making it's turn....")

    TICK_TACK_TOE_PLAYERS[chat_id]["field"] = make_bot_move(
        TICK_TACK_TOE_PLAYERS[chat_id]["field"],
        TICK_TACK_TOE_PLAYERS[chat_id]["bot_sign"],
    )

    if check_field_match(TICK_TACK_TOE_PLAYERS[chat_id]["field"]):
        game_end_text = make_winner_text(TICK_TACK_TOE_PLAYERS[chat_id])
        sent_message = bot.send_message(chat_id, game_end_text, reply_markup=MainMenuKeyboard)
        bot.register_next_step_handler(sent_message, handle_game_startup)
        return
    
    sent_message = bot.send_message(chat_id, "Your turn....", reply_markup=generate_keyboard_markup(TICK_TACK_TOE_PLAYERS[message.chat.id]["field"]))
    bot.register_next_step_handler(sent_message, handle_tick_tack_toe)


bot.infinity_polling()
