import random
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def generate_keyboard_markup(field: list[list[str]]) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [[], [], []]

    for row_index, row in enumerate(field):
        for col_index, col in enumerate(row):
            position = row_index * 3 + col_index
            sign = f"({position})" if not col else col
            buttons[row_index].append(KeyboardButton(sign))
    
    for button_list in buttons:
        markup.add(*button_list)

    return markup


def update_field_sign(field: list[list[str]], sign: str, sign_position: int) -> list[list[str]]:
    row_index = sign_position // 3
    col_index = (sign_position - row_index * 3) % 3

    field[row_index][col_index] = sign
    return field


def is_all_equal(line: str, sign):
    if len(line) < 3:
        return False

    return all([s == sign for s in line])


def is_fields_full(field: list[list[str]]) -> bool:
    if "" in field[0] + field[1] + field[2]:
        return False
    return True


def check_field_match(field: list[list[str]]) -> bool | str:
    if is_fields_full(field):
        return True

    for sign in ["X", "O"]:
        # Check horizontal rows
        for row in field:
            if is_all_equal(row, sign):
                return sign

        # Check vertical rows
        for i in range(3):
            column = ""
            for j in range(3):
                column += field[j][i]

            if is_all_equal(column, sign):
                return sign
        
        # Finally, check diagonals
        diagonal = ""
        for i in range(3):
            diagonal += field[i][i]
        
        if is_all_equal(diagonal, sign):
            return sign
        
        diagonal = (
            field[0][2] + field[1][1] + field[2][0]
        )
        if is_all_equal(diagonal, sign):
            return sign
    
    return False


def make_winner_text(data: dict) -> str:
    winner_sign: str | bool = check_field_match(data["field"])
    if not winner_sign:
        return "It's a tie!"

    return "You win =)" if winner_sign == data["player_sign"] else "You lose =("


def make_bot_move(field: list[list[str]], bot_sign: str) -> list[list[str]]:
    available_places = []
    for row_index, row in enumerate(field):
        for col_index, col in enumerate(row):
            if col == "":
                available_places.append((row_index, col_index))
    
    random.shuffle(available_places)
    selected_position = random.choice(available_places)

    field[selected_position[0]][selected_position[1]] = bot_sign

    return field
