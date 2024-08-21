from datetime import datetime
import random
import time
import asyncio

# import parser.utilits as ut
# from DB import sqlite_comands as sql
#
# from aiogram import Router, Bot
# from config import BOT_TOKEN
# from logger import logger as log

import MWB.parser.utilits as ut
from MWB.DB import sqlite_comands as sql

from aiogram import Router, Bot
from MWB.config import BOT_TOKEN
from MWB.logger import logger as log

router = Router()
bot = Bot(BOT_TOKEN)


async def wb_scrapper(discount, key: tuple):
    key_id, category, keyword, discount_proc, user_id = key[0], key[1], key[2], key[3], key[4]

    for count_page in range(1, 5):
        rand_proxy = await ut.random_proxy()

        url_ch_1 = 'https://search.wb.ru/'
        url_ch_3 = '&curr=rub&dest=-1255987&sort=popular&spp=30&resultset=catalog&suppressSpellcheck=false'
        if keyword == '0':
            url_ch_2 = f"catalog/{eval(category)[1]}/v2/catalog?ab_testing=false&appType=1&page={count_page}&{eval(category)[0]}"
        else:
            url_ch_2 = f"exactmatch/ru/common/v5/search?ab_testing=false&appType=1&page={count_page}&query={keyword}"

        constructor_url = url_ch_1 + url_ch_2 + url_ch_3

        try:
            response = await ut.wb_fetch_data(constructor_url, rand_proxy['http'])

        except Exception as e:
            log.error(f"Ошибка {e} при запросе.\nСтраница:{count_page}, "
                      f"Ключ:{keyword}, Категория {category[1]} Прокси{rand_proxy['http']}")
            continue
        else:
            pause = random.uniform(2, 5)
            await asyncio.sleep(pause)
            if response:
                try:
                    data_all = response['data']['products']
                except Exception as e:
                    log.error(f'Ошибка при попытке извлечь данные из словаря \n{e}')
                    continue
            else:
                log.info(f"Код не 200, подключаюсь через другой прокси! \n текущий прокси:{rand_proxy['http']}")
                time.sleep(20)
                continue

            for product in data_all:
                current_time = datetime.now().strftime('%d-%m-%Y')
                """ID товара"""
                product_id = product['id']
                """Стоимость товара"""
                if product.get('price'):
                    current_price = float(product['price']['product'])/100
                elif product['sizes'][0].get('price'):
                    current_price = float(product['sizes'][0]['price']['product'])/100
                else:
                    log.info(f'''Товар: {product['name']} {product['id']} не найден''')
                    continue

                product_data = await sql.get_product(product_id)
                if product_data:
                    product_key_id = await sql.get_favourite_product(product_id=product_id, key_id=key_id)
                    p_k_id, favourites_status = product_key_id[0], product_key_id[3]

                    if not favourites_status:
                        primary_price = product_data[2]
                        discount_proc = ((primary_price / current_price) * 100) - 100

                        if discount_proc >= 20:
                            log.debug(f"{product['name']} упал в цене. Скидка: {discount_proc}%.")

                        if discount_proc >= discount:
                            await sql.update_favourite(p_k_id)
                            await bot.send_message(chat_id=user_id,
                                                   text=f"{product['name']} упал в цене. Цена при добавлении в базу "
                                                        f"данных бота - {primary_price},\nтекущая цена {current_price}"
                                                        f"\nРеальная скидка - {discount_proc}%\n"
                                                        f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx")
                else:
                    await sql.add_product(product_id=product_id, reg_time=current_time,
                                          primary_price=current_price, key=key_id)


# async def worker(semaphore, lst_keyword, user_id):
#     async with semaphore:
#         await wb_scrapper(lst_keyword, user_id)


if __name__ == "__main__":
    lst_keyword = [('Джинсы синие', 30), ('Кабачек', 30)]
    # asyncio.run(wb_scrapper(lst_keyword, 674796107))
    # asyncio.run(bot.send_message(chat_id=674796107, text='{/prod_name} упал в цене. \nЦена при добавлеении в БД - {last_price}'))
