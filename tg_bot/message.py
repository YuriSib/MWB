from tg_bot.heandlers import bot


async def send_message_to_user(user_id, prod_name, prod_id, last_price, cur_price):
    await bot.send_message(chat_id=user_id, text=f'{prod_name} упал в цене. \nЦена при добавлеении в БД - {last_price}'
                                                 f'текущая цена {cur_price}\n '
                                                 f'https://www.wildberries.ru/catalog/{prod_id}/detail.aspx')


async def message_to_favourites_prod(user_id, prod_name, prod_id, last_price, cur_price):
    await bot.send_message(chat_id=user_id, text=f'{prod_name} снова упал в цене. \nЦена при добавлеении в избранное - '
                                                 f'{last_price}, текущая цена {cur_price}\n '
                                                 f'https://www.wildberries.ru/catalog/{prod_id}/detail.aspx')
