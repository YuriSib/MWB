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
                        reg_time TEXT,
                        parsing_status BOOL)''')
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
                         "VALUES (?, ?, ?)", (product_id, reg_time, primary_price))
    await cursor.execute('''DELETE FROM favourites_products WHERE id = ?''', (product_id,))
    await conn.commit()


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


async def update_key_word_link(token_id, word=None, link=None):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        if word:
            await conn.execute(f"UPDATE keys SET keyword = '{word}' WHERE id = {token_id}")
        else:
            await conn.execute(f"UPDATE keys SET key_link = '{link}' WHERE id = {token_id}")
        await conn.commit()


async def update_token_name(token_id, name):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        await conn.execute(f"UPDATE keys SET token_name = '{name}' WHERE id = {token_id}")
        await conn.commit()


async def update_discount(token_id, discount):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        await conn.execute(f"UPDATE keys SET discount = '{discount}' WHERE id = {token_id}")
        await conn.commit()


async def update_parsing_status(tg_id, status):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        await conn.execute(f"UPDATE users SET parsing_status = '{status}' WHERE tg_id = {tg_id}")
        await conn.commit()


async def get_parsing_status(tg_id):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        result = await conn.execute_fetchall("SELECT parsing_status FROM users WHERE tg_id = ?", (tg_id,))
        return result


async def get_list_keyword(tg_id):
    await check_db()
    async with aiosqlite.connect('../users.db') as conn:
        result = await conn.execute_fetchall("SELECT keyword, discount FROM keys WHERE user_id = ?", (tg_id,))
        return result


if __name__ == "__main__":
    product_id_ = 12345
    current_time = datetime.now().strftime('%d-%m-%Y')
    tg_id = 674796107

    # asyncio.run(new_field('parsing_status'))
    print(asyncio.run(get_list_keyword(tg_id)))
    # # update_product(123456, 170)
    # print(asyncio.run(get_product(product_id_)))
