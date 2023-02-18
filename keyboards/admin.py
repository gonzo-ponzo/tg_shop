from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


button_1 = KeyboardButton("/Войти")
button_2 = KeyboardButton("/Загрузить")
button_3 = KeyboardButton("/Удалить")
button_4 = KeyboardButton("/Остатки")
button_5 = KeyboardButton("/Назад")

keyboard_no_login = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_no_login.add(button_1)

keyboard_with_login = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_with_login.row(button_2, button_3).add(button_4).add(button_5)


def keyboard_delete_product(product):
    product = product[0]
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(f"Удалить", callback_data=f"del {product}")
    keyboard.add(button)
    return keyboard


def keyboard_update_product(product):
    product = product[0]
    keyboard = InlineKeyboardMarkup()
    button_1 = InlineKeyboardButton("+1", callback_data=f"upd {product}_+1")
    button_2 = InlineKeyboardButton("-1", callback_data=f"upd {product}_-1")
    button_3 = InlineKeyboardButton("+5", callback_data=f"upd {product}_+5")
    button_4 = InlineKeyboardButton("-5", callback_data=f"upd {product}_-5")
    button_5 = InlineKeyboardButton("+10", callback_data=f"upd {product}_+10")
    button_6 = InlineKeyboardButton("-10", callback_data=f"upd {product}_-10")
    keyboard.row(button_1, button_2).row(button_3, button_4).row(button_5, button_6)
    return keyboard
