from datetime import datetime, timedelta
from MWB.DB import sqlite_comands as sql
from MWB.tg_bot import keyboards as kb

from MWB.logger import logger as log


async def subs_calculation(date, q_day):
    date = datetime.strptime(date, "%d-%m-%Y %H:%M:%S")
    date_end = date + timedelta(days=q_day)
    current_date = datetime.now()
    remaining_days = (date_end - current_date).days + 1

    if remaining_days > 0:
        return remaining_days
    elif remaining_days == 0:
        return "Подписка истекает сегодня."
    else:
        return "Подписка истекла."


async def choice_category_lvl(lvl: int, callback, state, bot):
    lvl_id = int(callback.data.replace(f'lvl{lvl}_', ''))

    data = await state.get_data()
    catalog_tree = data['catalog_tree']
    id_dict = data['id_dict']
    token_id = data['token_id']

    current_category = 0
    if lvl == 1:
        current_category = catalog_tree[lvl_id]
        await state.update_data(lvl_1_id=lvl_id)
    elif lvl == 2:
        lvl_1_id = data['lvl_1_id']
        current_category = catalog_tree[lvl_1_id][lvl_id]
        await state.update_data(lvl_2_id=lvl_id)
    elif lvl == 3:
        lvl_1_id, lvl_2_id = data['lvl_1_id'], data['lvl_2_id']
        current_category = catalog_tree[lvl_1_id][lvl_2_id][lvl_id]
        await state.update_data(lvl_3_id=lvl_id)
    elif lvl == 4:
        lvl_1_id, lvl_2_id, lvl_3_id = data['lvl_1_id'], data['lvl_2_id'], data['lvl_3_id']
        current_category = catalog_tree[lvl_1_id][lvl_2_id][lvl_3_id][lvl_id]

    if type(current_category) is dict:
        categories = [id_ for id_ in current_category]
        category_id = [(id_dict[id_], id_) for id_ in categories]

        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=callback.from_user.id, text='Выберите нужную категорию из списка',
                               reply_markup=await kb.list_to_inline(lvl + 1, category_id))
    elif type(current_category) is tuple:
        await sql.update_key(token_id=token_id, category=current_category)
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        await sql.update_token_name(token_id=token_id, name='Категория - '+id_dict[lvl_id])

        sale_percent = (await sql.get_a_token(token_id))[0][4]
        if sale_percent:
            await bot.send_message(chat_id=callback.from_user.id, reply_markup=await kb.key_editor(token_id),
                                   text=f'Вы настроили токен на категорию {id_dict[lvl_id]}.')
        else:
            return id_dict[lvl_id]


if __name__ == "__main__":
    print(subs_calculation('15-06-2024', 5))
