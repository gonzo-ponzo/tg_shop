from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from environs import Env
from database.db import sql_add, sql_read_catalog, sql_delete, sql_update
from keyboards.admin import (
    keyboard_no_login,
    keyboard_with_login,
    keyboard_delete_product,
    keyboard_update_product,
)
from bot_init import bot


env = Env()
env.read_env()
PASSWORD = env.str("PASSWORD")
ID = None


class FSMSetAdmin(StatesGroup):
    password = State()


class FSMAdmin(StatesGroup):
    name = State()
    price = State()
    amount = State()
    photo = State()


async def admin_menu(message: types.Message):
    if message.from_user.id == ID:
        await message.answer("Что хочешь?", reply_markup=keyboard_with_login)
    else:
        await message.answer("Что хочешь?", reply_markup=keyboard_no_login)


async def set_moderator(message: types.Message):
    await FSMSetAdmin.password.set()
    await message.answer("Введите пароль.")


async def enter_password(message: types.Message, state=FSMContext):
    global ID
    if message.text == PASSWORD:
        ID = message.from_user.id
        await message.answer("Приветствую!", reply_markup=keyboard_with_login)
    else:
        await message.answer("Неверный пароль!")
    await state.finish()


async def new_product(message: types.Message):
    if message.from_user.id == ID:
        await FSMAdmin.name.set()
        await message.reply("Введи наименование продукта.")


async def new_product_name(message: types.Message, state=FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data["name"] = message.text
        await FSMAdmin.next()
        await message.reply("Введи стоимость продукта.")


async def new_product_price(message: types.Message, state=FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data["price"] = int(message.text)
        await FSMAdmin.next()
        await message.reply("Введи количество.")


async def new_product_amount(message: types.Message, state=FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data["amount"] = int(message.text)
        await FSMAdmin.next()
        await message.reply("Загрузи фотографию.")


async def new_product_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data["photo"] = message.photo[0].file_id
        await sql_add(state)
        await state.finish()


async def delete_product(message: types.Message):
    if message.from_user.id == ID:
        products = await sql_read_catalog()
        for product in products:
            await bot.send_message(
                message.from_user.id,
                text=f"{product[0]}",
                reply_markup=keyboard_delete_product(product),
            )


async def update_product(message: types.Message):
    if message.from_user.id == ID:
        products = await sql_read_catalog()
        for product in products:
            await bot.send_message(
                message.from_user.id,
                text=f"{product[0]}",
                reply_markup=keyboard_update_product(product),
            )


async def del_callback(callback: types.CallbackQuery):
    product = callback.data.replace("del ", "")
    await sql_delete(product)
    await callback.answer(text=f"{product} - удаление прошло успешно.", show_alert=True)


async def upd_callback(callback: types.CallbackQuery):
    print(callback.data.replace("upd ", "").split("_"))
    product, count = callback.data.replace("upd ", "").split("_")
    await sql_update(product, count)
    await callback.answer(text=f"{product} {count}.")


async def new_product_cancel(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply("Создание нового продукта отменено.")


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_menu, commands="Админ")
    dp.register_message_handler(set_moderator, commands="Войти", state=None)
    dp.register_message_handler(enter_password, state=FSMSetAdmin.password)
    dp.register_message_handler(new_product_cancel, state="*", commands="Отмена")
    dp.register_message_handler(
        new_product_cancel, Text(equals="Отмена", ignore_case=True), state="*"
    )
    dp.register_callback_query_handler(del_callback, Text(startswith="del "))
    dp.register_message_handler(delete_product, commands="Удалить")
    dp.register_callback_query_handler(upd_callback, Text(startswith="upd "))
    dp.register_message_handler(update_product, commands="Остатки")
    dp.register_message_handler(new_product, commands="Загрузить", state=None)
    dp.register_message_handler(new_product_name, state=FSMAdmin.name)
    dp.register_message_handler(new_product_price, state=FSMAdmin.price)
    dp.register_message_handler(new_product_amount, state=FSMAdmin.amount)
    dp.register_message_handler(
        new_product_photo, content_types=["photo"], state=FSMAdmin.photo
    )
