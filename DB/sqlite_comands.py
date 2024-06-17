import sqlite3
from sqlite3 import Error
import json
import os
from datetime import datetime
import asyncio
import aiosqlite


async def check_db():
    async with aiosqlite.connect('../users.db') as conn:
        cursor = await conn.cursor()
        await cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                        (tg_id INTEGER PRIMARY KEY, 
                        name TEXT, 
                        reg_time TEXT)''')
        await cursor.execute('''CREATE TABLE IF NOT EXISTS products
                        (product_id INTEGER PRIMARY KEY, 
                        reg_time TEXT,
                        primary_price INTEGER)''')
        await cursor.execute('''CREATE TABLE IF NOT EXISTS favourites_products
                        (product_id INTEGER PRIMARY KEY, 
                        reg_time TEXT,
                        primary_price INTEGER,
                        call_price INTEGER)''')
        await cursor.execute('''CREATE TABLE IF NOT EXISTS keys
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        token_name TEXT,
                        key_link TEXT,
                        keyword TEXT,
                        discount INTEGER,
                        reg_time TEXT,
                        subs_period TEXT,
                        user_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users(tg_id))''')


async def get_product(product_id):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        cursor = await conn.cursor()
        await cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        product = await cursor.fetchone()
        if product:
            return product
        else:
            return False


async def add_product(product_id, reg_time, primary_price):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        cursor = await conn.cursor()
        await cursor.execute("INSERT INTO products (product_id, reg_time, primary_price) VALUES (?, ?, ?)",
                             (product_id, reg_time, primary_price))
        await conn.commit()
        await conn.close()


async def add_to_favourites(product_id, reg_time, primary_price, call_price):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        cursor = await conn.cursor()
        await cursor.execute("INSERT INTO favourites_products (product_id, reg_time, primary_price, call_price) "
                             "VALUES (?, ?, ?, ?)", (product_id, reg_time, primary_price, call_price))
        await cursor.execute('''DELETE FROM products WHERE id = ?''', (product_id,))
        await conn.commit()


async def return_to_prod(product_id, reg_time, primary_price):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        cursor = await conn.cursor()
    await cursor.execute("INSERT INTO products (product_id, reg_time, primary_price) "
                   "VALUES (?, ?, ?, ?)", (product_id, reg_time, primary_price))
    await cursor.execute('''DELETE FROM favourites_products WHERE id = ?''', (product_id,))
    await conn.commit()


async def add_keyword(keyword, discount):
    pass


async def add_key_link(key_link, discount):
    pass


async def check_user(tg_id):
    async with aiosqlite.connect('../users.db') as conn:
        result = await conn.execute_fetchall("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
    return bool(result)


async def add_user(name, tg_id):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        cursor = await conn.cursor()
        time = datetime.now().strftime('%d-%m-%Y')
        await cursor.execute("INSERT INTO users (tg_id, name, reg_time) VALUES (?, ?, ?)", (tg_id, name, time))
        await conn.commit()


async def get_token(tg_id):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        result = await conn.execute_fetchall("SELECT * FROM keys WHERE user_id = ?", (tg_id,))
        return result


async def delete_token(token_id):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        await conn.execute('''DELETE FROM keys WHERE id = ?''', (token_id,))
        await conn.commit()


async def add_token(user_id, period):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        time = datetime.now().strftime('%d-%m-%Y')
        await conn.execute("INSERT INTO keys (reg_time, subs_period, user_id) VALUES (?, ?, ?)",
                           (time, period, user_id))
        await conn.commit()


if __name__ == "__main__":
    product_id_ = 12345
    current_time = datetime.now().strftime('%d-%m-%Y')
    tg_id = 674796107

    # asyncio.run(add_product(product_id_, current_time, 2545670))
    print(asyncio.run(get_token(tg_id)))
    # # update_product(123456, 170)
    # print(asyncio.run(get_product(product_id_)))
