import requests
from datetime import datetime
import random
import time
import aiohttp
import asyncio

import utilits as ut
from DB import sqlite_comands as sql
from tg_bot.message import send_message_to_user


async def wb_scrapper(lst_keyword: list[tuple]):
    while True:
        current_keys_num = 1
        for row in lst_keyword:
            current_keys_num += 1
            KEY_WORD = row[0]
            DISCOUNT_PROC = row[1]

            for count_page in range(1, 5):
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
                        print(200)
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
                        else:
                            current_price = float(product['sizes'][0]['price']['product'])/100

                        product_data = sql.get_product(product_id)

                        if product_data:
                            reg_time, primary_price = product_data[1], product_data[2]
                            discount_proc = ((primary_price/current_price)*100)-100
                            if discount_proc >= DISCOUNT_PROC:
                                await sql.add_to_favourites(product_id=product_id, reg_time=reg_time,
                                                            primary_price=primary_price, call_price=current_price)
                                send_message_to_user(old_price=primary_price, new_price=current_price, user_id=1234)
                        else:
                            await sql.add_product(product_id=product_id, reg_time=current_time, primary_price=current_price)


if __name__ == "__main__":
    lst_keyword = [('Джинсы синие', 30), ('Кабачек', 30)]
    asyncio.run(wb_scrapper(lst_keyword))

