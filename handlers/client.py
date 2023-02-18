from aiogram import types, Dispatcher
from aiogram.types.message import ContentType
from aiogram.dispatcher import FSMContext
from bot_init import bot
from keyboards.client import keyboard, keyboard_buy_product
from database.db import (
    sql_send_catalog,
    sql_read_catalog,
    get_price,
    check_amount,
    sql_sold,
)
from aiogram.dispatcher.filters.state import State, StatesGroup
from environs import Env


env = Env()
env.read_env()
PAYMENT = env.str("PAYMENT")


class FSMBuy(StatesGroup):
    name = State()
    amount = State()


async def command_start(message: types.Message) -> None:
    await message.answer("Чем помочь?", reply_markup=keyboard)


async def catalog(message: types.Message) -> None:
    await sql_send_catalog(message)


async def buy(message: types.Message) -> None:
    await FSMBuy.name.set()
    products = await sql_read_catalog()
    await message.reply(
        "Что Вы хотите купить?", reply_markup=await keyboard_buy_product(products)
    )


async def buy_product_name(callback: types.CallbackQuery, state=FSMContext) -> None:
    async with state.proxy() as data:
        data["product"] = callback.data.replace("buy ", "")
    await FSMBuy.next()
    await callback.message.reply("Введи количество.")


async def buy_product_amount(message: types.Message, state=FSMContext) -> None:
    async with state.proxy() as data:
        data["amount"] = int(message.text)
        product = data["product"]
        amount = data["amount"]
        if await check_amount(product, amount):
            price = await get_price(product, amount)
            await bot.send_invoice(
                message.from_user.id,
                title=f"{product}",
                description=f"Покупка {product} - {amount} шт.",
                provider_token=PAYMENT,
                currency="rub",
                is_flexible=False,
                prices=[price],
                payload=f"{product} - {amount} шт.",
            )
        else:
            await message.reply("Вы превысили доступный остаток!")
    await state.finish()


async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


async def successful_payment(message: types.Message):
    from .admin import ID

    print(ID)
    await bot.send_message(
        message.from_user.id,
        f"Платёж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!",
    )
    await sql_sold(message.successful_payment.invoice_payload)
    username = message.from_user.username
    if not username:
        username = ""
    name = message.from_user.first_name
    await bot.send_message(
        ID,
        text=f"@{username}\n {name}\n Совершена покупка на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency}\n {message.successful_payment.invoice_payload}",
    )


def register_client_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=["start", "help", "Назад"])
    dp.register_message_handler(catalog, commands="Каталог")
    dp.register_message_handler(buy, commands="Купить", state=None)
    dp.register_callback_query_handler(buy_product_name, state=FSMBuy.name)
    dp.register_message_handler(buy_product_amount, state=FSMBuy.amount)
    dp.register_pre_checkout_query_handler(pre_checkout_query, lambda query: True)
    dp.register_message_handler(
        successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT
    )
