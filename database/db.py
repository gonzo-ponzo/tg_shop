import sqlite3 as sq
from bot_init import bot
from aiogram import types
from aiogram.dispatcher.filters.state import State


def connect_db() -> None:
    global db, curr
    db = sq.connect("database.db")
    curr = db.cursor()
    if db:
        print("DATABASE CONNECTED")
    db.execute(
        "CREATE TABLE IF NOT EXISTS products(name TEXT PRIMARY KEY, price INTEGER, amount INTEGER, image TEXT)"
    )
    db.commit()


async def sql_add(state: State) -> None:
    async with state.proxy() as data:
        curr.execute("INSERT INTO products VALUES (?, ?, ?, ?)", tuple(data.values()))
        db.commit()


async def sql_send_catalog(message: types.Message) -> None:
    for product in curr.execute("SELECT * FROM products").fetchall():
        await bot.send_photo(
            message.from_user.id,
            product[3],
            f"{product[0]}\nСтоимость: {product[1]} руб\nВ наличии: {product[2]}",
        )


async def sql_read_catalog() -> tuple:
    return curr.execute("SELECT * FROM products").fetchall()


async def sql_delete(product: str) -> None:
    curr.execute("DELETE FROM products WHERE name == ?", (product,))
    db.commit()


async def sql_update(product: str, count: int) -> None:
    curr.execute(
        "UPDATE products SET amount = amount + ? WHERE name == ?", (count, product)
    )
    db.commit()


async def get_price(product: str, count: int) -> types.LabeledPrice:
    product_info = curr.execute(
        "SELECT * FROM products WHERE name == ?", (product,)
    ).fetchone()
    return types.LabeledPrice(
        label=f"{product_info[0]}", amount=product_info[1] * 100 * count
    )


async def check_amount(product: str, count: int) -> bool:
    product_info = curr.execute(
        "SELECT * FROM products WHERE name == ?", (product,)
    ).fetchone()
    if product_info[2] < count:
        return False
    return True


async def sql_sold(invoice: str) -> None:
    product, count = invoice.split(" - ")
    count = count.split(" ")[0]
    curr.execute(
        "UPDATE products SET amount = amount - ? WHERE name == ?", (count, product)
    )
    db.commit()
