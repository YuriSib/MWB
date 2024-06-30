from datetime import datetime
import random
import time
import asyncio

import parser.utilits as ut
from DB import sqlite_comands as sql

from aiogram import Router, Bot
from config import BOT_TOKEN
import logger

router = Router()
bot = Bot(BOT_TOKEN)


async def wb_scrapper(lst_keyword: list[tuple], user_id):
    logger.cycle_logger.info(f"Цикл для пользователя {user_id} запущен!")
    current_keys_num = 1
    for row in lst_keyword:
        if not await sql.get_parsing_status(user_id):
            return 'Мониторинг приостановлен!'

        if not row[0] or not row[1]:
            continue

        current_keys_num += 1
        KEY_WORD = row[0]
        DISCOUNT_PROC = row[1]

        for count_page in range(1, 5):
            if not await sql.get_parsing_status(user_id):
                return 'Мониторинг приостановлен!'

            try:
                rand_proxy = await ut.random_proxy()
            except Exception as e:
                print(f'Произошла ошибка {e}')
                continue
            constructor_url = (f"https://search.wb.ru/exactmatch/ru/common/v5/search?ab_testing=false&appType=1&"
                                f"curr=rub&dest=-1257786&page={count_page}&query={KEY_WORD}"
                                f"&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false")
            print(count_page, KEY_WORD)
            try:
                response = await ut.wb_fetch_data(constructor_url, rand_proxy['http'])

            except Exception as e:
                print(f"Ошибка {e} произошла при запросе")
                with open(f'requests_log.txt', 'a', encoding='utf-8') as file:
                    file.write(
                        f"\n{datetime.now().ctime()}\nОшибка {e} при запросе."
                        f" \nСтраница:{count_page}, Ключ:{KEY_WORD}, Прокси{rand_proxy['http']} \n")
                if type(e) == 'ProxyError':
                    print(f"ProxyError: {rand_proxy['http']}")
                continue
            else:
                pause = random.uniform(2, 5)
                time.sleep(pause)
                if response:
                    print(user_id)
                    try:
                        data_all = response['data']['products']
                    except Exception as e:
                        print(f'В строке data_all = data_all.json() произошла ошибка \n{e}')
                        continue
                else:
                    print(f"Код не {200}, подключаюсь через другой прокси! \n "
                          f"текущий прокси:{rand_proxy['http']}")
                    time.sleep(20)
                    continue

                for product in data_all:
                    current_time = datetime.now().strftime('%d-%m-%Y')

                    product_id = product['id']

                    if product.get('price'):
                        current_price = float(product['price']['product'])/100
                    elif product['sizes'][0].get('price'):
                        current_price = float(product['sizes'][0]['price']['product'])/100
                    else:
                        print(f'''Товар: {product['name']} {product['id']} не найден''')
                        continue

                    product_data = await sql.get_product(product_id)
                    favourite_product_data = await sql.get_favourite_product(product_id, user_id)

                    if favourite_product_data:
                        reg_time, last_price = favourite_product_data[1], favourite_product_data[4]
                        discount_proc = ((last_price / current_price) * 100) - 100
                        if discount_proc < 0:
                            await sql.return_to_prod(product_id, reg_time, last_price)
                        elif discount_proc > 10:
                            await sql.update_favourite_product(product_id, current_price, user_id)
                            await bot.send_message(chat_id=user_id,
                                                   text=f"{product['name']} снова упал в цене. Цена при добавлении в избранное - {last_price},"
                                                        f" текущая цена {current_price}\n "
                                                        f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx")
                    elif product_data:
                        reg_time, primary_price = product_data[1], product_data[2]
                        discount_proc = ((primary_price/current_price)*100)-100
                        if discount_proc >= 20:
                            logger.cycle_logger.info(f"{product['name']} упал в цене. Скидка: {discount_proc}%.")
                        if discount_proc >= DISCOUNT_PROC:
                            await bot.send_message(chat_id=user_id,
                                                   text=f"{product['name']} упал в цене."
                                                        f"Цена при добавлеении в БД - {primary_price} р., "
                                                        f"текущая цена {current_price}р.\n"
                                                        f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx")

                            await sql.add_to_favourites(product_id=product_id, reg_time=reg_time,
                                                        primary_price=primary_price, call_price=current_price)
                    else:
                        await sql.add_product(product_id=product_id, reg_time=current_time,
                                              primary_price=current_price)


async def worker(semaphore, lst_keyword, user_id):
    async with semaphore:
        await wb_scrapper(lst_keyword, user_id)


if __name__ == "__main__":
    lst_keyword = [('Джинсы синие', 30), ('Кабачек', 30)]
    asyncio.run(wb_scrapper(lst_keyword, 674796107))
    # asyncio.run(bot.send_message(chat_id=674796107, text='{/prod_name} упал в цене. \nЦена при добавлеении в БД - {last_price}'))

