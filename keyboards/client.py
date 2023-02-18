from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


button_1 = KeyboardButton("/Каталог")
button_2 = KeyboardButton("/Админ")
button_3 = KeyboardButton("/Купить")
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(button_1).add(button_2).add(button_3)


async def keyboard_buy_product(products: tuple) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for product in products:
        button = InlineKeyboardButton(
            f"{product[0]}", callback_data=f"buy {product[0]}"
        )
        keyboard.add(button)
    return keyboard
