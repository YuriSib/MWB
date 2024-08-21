from aiosqlite import Error
from datetime import datetime
import asyncio
import aiosqlite

# import logger as log
# from config import PATH_TO_BD

import MWB.logger as log
from MWB.config import PATH_TO_BD


async def check_db():
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        cursor = await conn.cursor()
        """Создаю модели данных"""
        await cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                        (tg_id INTEGER PRIMARY KEY, 
                        name TEXT, 
                        reg_time TEXT,
                        ban_status BOOL)''')

        await cursor.execute('''CREATE TABLE IF NOT EXISTS products
                        (product_id INTEGER PRIMARY KEY, 
                        reg_time TEXT,
                        primary_price INTEGER)''')

        # await cursor.execute('''CREATE TABLE IF NOT EXISTS favourites_products
        #                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
        #                 product_id INTEGER,
        #                 reg_time TEXT,
        #                 primary_price INTEGER,
        #                 call_price INTEGER,
        #                 user_id INTEGER)''')

        await cursor.execute('''CREATE TABLE IF NOT EXISTS keys
                                (key_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                token_name TEXT,
                                key_category TEXT,
                                keyword TEXT,
                                discount INTEGER,
                                reg_time TEXT,
                                subs_period TEXT,
                                user_id INTEGER,
                                FOREIGN KEY (user_id) REFERENCES users(tg_id))''')

        await cursor.execute('''CREATE TABLE IF NOT EXISTS product_key
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                product_id INTEGER,
                                key_id INTEGER,
                                favourites INTEGER DEFAULT 0,
                                FOREIGN KEY (product_id) REFERENCES products(product_id),
                                FOREIGN KEY (key_id) REFERENCES products(key_id))''')


async def add_product(product_id, reg_time, primary_price, key):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        cursor = await conn.cursor()
        try:
            await cursor.execute("INSERT INTO products (product_id, reg_time, primary_price) VALUES (?, ?, ?)",
                                 (product_id, reg_time, primary_price))
            await cursor.execute("INSERT INTO product_key (product_id, key_id) VALUES (?, ?)", (product_id, key))
        except Error as e:
            print(f"Ошибка при добавлении товара в БД {e}")
        finally:
            await conn.commit()
            await conn.close()


async def add_to_favourites(product_id, reg_time, primary_price, call_price, user_id):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        cursor = await conn.cursor()
        try:
            await cursor.execute("INSERT INTO favourites_products (product_id, reg_time, primary_price, call_price, user_id) "
                                 "VALUES (?, ?, ?, ?, ?)", (product_id, reg_time, primary_price, call_price, user_id))
        except Error as e:
            print(f"Ошибка при добавлении товара в БД {e} (add_to_favourites)")
        else:
            await cursor.execute('''DELETE FROM products WHERE product_id = ?''', (product_id,))
            await conn.commit()


async def add_user(name, tg_id):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        cursor = await conn.cursor()
        time = datetime.now().strftime('%d-%m-%Y')
        await cursor.execute("INSERT INTO users (tg_id, name, reg_time) VALUES (?, ?, ?)", (tg_id, name, time))
        await conn.commit()


async def add_token(user_id, period, username):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        await conn.execute("INSERT OR IGNORE INTO users (tg_id, name, reg_time) VALUES (?, ?, ?)",
                           (user_id, username, time))
        await conn.execute("INSERT INTO keys (reg_time, subs_period, user_id) VALUES (?, ?, ?)",
                           (time, period, user_id))
        await conn.commit()


async def add_product_key(product, key):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        cursor = await conn.cursor()
        await cursor.execute("INSERT INTO product_key (product_id, key_id) VALUES (?, ?)", (product, key))
        await conn.commit()


async def get_favourite_product(product_id, key_id):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        cursor = await conn.cursor()
        await cursor.execute(f"""SELECT *
                                FROM product_key
                                WHERE product_id = {product_id} AND key_id = {key_id};""")
        product_key = await cursor.fetchone()
        if product_key:
            return product_key
        else:
            return False


async def get_product(product_id):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        cursor = await conn.cursor()
        await cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        product = await cursor.fetchone()
        if product:
            return product
        else:
            return False


async def get_parsing_status(tg_id):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        result = await conn.execute_fetchall("SELECT parsing_status FROM users WHERE tg_id = ?", (tg_id,))
        return result


async def get_list_keyword(tg_id):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        result = await conn.execute_fetchall("SELECT keyword, discount FROM keys WHERE user_id = ?", (tg_id,))
        return result


async def get_user_keys():
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        user_list = [user[0] for user in await conn.execute_fetchall(f"SELECT tg_id FROM users")]

        user_keys = {}
        for user in user_list:
            key_list = await conn.execute_fetchall(f"SELECT keyword, discount FROM keys WHERE user_id = ?",
                                                   (user,))
            key_list = [key for key in key_list if key[0] and key[1]]

            user_keys[user] = key_list

        return user_keys


async def get_token(tg_id):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        result = await conn.execute_fetchall("SELECT * FROM keys WHERE user_id = ?", (tg_id,))
        return result


async def get_a_token(token_id):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        result = await conn.execute_fetchall("SELECT * FROM keys WHERE key_id = ?", (token_id,))
        return result


async def get_tokens():
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        result = await conn.execute_fetchall("SELECT * FROM keys")
        return result


async def update_favourite_status(product_id, call_price, user_id):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        await conn.execute(f"UPDATE favourites_products SET call_price = '{call_price}' "
                           f"WHERE product_id = {product_id} and user_id = {user_id}")

        await conn.commit()


async def cancel_favourite(product_id, reg_time, primary_price):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        cursor = await conn.cursor()
    await cursor.execute("INSERT INTO products (product_id, reg_time, primary_price) "
                         "VALUES (?, ?, ?)", (product_id, reg_time, primary_price))
    await cursor.execute('''DELETE FROM favourites_products WHERE id = ?''', (product_id,))
    await conn.commit()


async def check_user(tg_id):
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        result = await conn.execute_fetchall("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
    return bool(result)


async def delete_token(token_id):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        await conn.execute('''DELETE FROM keys WHERE id = ?''', (token_id,))
        await conn.commit()


async def update_key(token_id, word=None, category=None):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        if word:
            await conn.execute(f"UPDATE keys SET keyword = '{word}' WHERE key_id = {token_id}")
            await conn.execute(f"UPDATE keys SET key_category = '0' WHERE key_id = {token_id}")
        else:
            await conn.execute("UPDATE keys SET key_category = ? WHERE key_id = ?", (str(category), token_id))
            await conn.execute(f"UPDATE keys SET keyword = '0' WHERE key_id = {token_id}")
        await conn.commit()


async def update_token_name(token_id, name):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        await conn.execute(f"UPDATE keys SET token_name = '{name}' WHERE key_id = {token_id}")
        await conn.commit()


async def update_discount(token_id, discount):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        await conn.execute(f"UPDATE keys SET discount = '{discount}' WHERE key_id = {token_id}")
        await conn.commit()


async def update_favourite(product_key_id):
    await check_db()
    async with aiosqlite.connect(PATH_TO_BD) as conn:
        await conn.execute(f"UPDATE product_key SET favourites = 1 WHERE id = (?,)", (product_key_id,))
        await conn.commit()


if __name__ == "__main__":
    product_id_ = 2282783026
    current_time = datetime.now().strftime('%d-%m-%Y')
    tg_id = 674796107

    # log.product_logger.info("Тестирую товары из другого модуля")

    # asyncio.run(add_product(product_id_, current_time, tg_id))
    print(asyncio.run(get_list_keyword(tg_id)))
    # print(asyncio.run(get_user_keys()))
    # # update_product(123456, 170)
    # print(asyncio.run(get_product(product_id_)))
