from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from DB import sqlite_comands as sql
from MWB.DB import sqlite_comands as sql


registration = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Зарегистрироваться', callback_data='Регистрация'),
     InlineKeyboardButton(text='Справка', callback_data='Справка')],
    [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
])

# main_menu = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text='Личный кабинет', callback_data='Личный_кабинет')],
#     [InlineKeyboardButton(text='Задать ключи', callback_data='Ключи'),
#      InlineKeyboardButton(text='Задать категории', callback_data='Категории')]
# ])

admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Запустить мониторинг', callback_data='Запустить_мониторинг'),
     InlineKeyboardButton(text='Остановить мониторинг', callback_data='Остановить_мониторинг')],
    [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
])

back_to_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
])

personal_cabinet = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Мои токены', callback_data='Мои_токены'),
     InlineKeyboardButton(text='Купить токены', callback_data='Купить_токены')],
    [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
])

# personal_cabinet_2 = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text='Мои токены', callback_data='Мои_токены'),
#      InlineKeyboardButton(text='Купить токены', callback_data='Купить_токены')],
#     [InlineKeyboardButton(text='Остановить мониторинг', callback_data='Остановить_мониторинг')]
# ])

key = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Задать ключ', callback_data='Задать_ключ'),
     InlineKeyboardButton(text='Задать категорию', callback_data='Задать_категорию')],
    [InlineKeyboardButton(text='Переименовать токен', callback_data='Переименовать_токен')],
    [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
])

pay_tokens = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1 токен на 7 дней(30р.)', callback_data='оплатить_1_на_7'),
     InlineKeyboardButton(text='3 токена на 7 дней(60р.)', callback_data='оплатить_3_на_7')],
    [InlineKeyboardButton(text='1 токен на 14 дней(50р.)', callback_data='оплатить_1_на_14'),
     InlineKeyboardButton(text='3 токена на 14 дней(100р.)', callback_data='оплатить_3_на_14')],
    [InlineKeyboardButton(text='1 токен на 30 дней(80р.)', callback_data='оплатить_1_на_30'),
     InlineKeyboardButton(text='3 токена на 30 дней(160р.)', callback_data='оплатить_3_на_30')],
    [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
])

# category = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text='Введите номер категории из списка', callback_data='Ввод_категории')],
#     [InlineKeyboardButton(text='На категорию вверх', callback_data='На_категорию_вверх')],
#     [InlineKeyboardButton(text='Выбрать категорию', callback_data='Выбрать категорию')],
# ])

percent = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Укажите процент', callback_data='Укажите_процент')],
    [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
])


# async def cabinet_keyboard(tg_id: int) -> InlineKeyboardMarkup:
#     buttons = [
#         [InlineKeyboardButton(text='Мои токены', callback_data='Мои_токены'),
#          InlineKeyboardButton(text='Купить токены', callback_data='Купить_токены')]]
#     if await sql.get_parsing_status(tg_id):
#         buttons.append([InlineKeyboardButton(text='Остановить мониторинг по всем ключам',
#                                              callback_data='Остановить_мониторинг')])
#     else:
#         buttons.append([InlineKeyboardButton(text='Запустить мониторинг по всем ключам',
#                                              callback_data='Запустить_мониторинг')])
#     return InlineKeyboardMarkup(inline_keyboard=buttons)


async def token_keyboard(tokens: dict) -> InlineKeyboardMarkup:
    row = []
    for id_, name in tokens.items():
        row.append([InlineKeyboardButton(text=name, callback_data=f'токен_{id_}')])
    row.append([InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')])

    return InlineKeyboardMarkup(inline_keyboard=row)


async def key_editor(token_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Задать ключ', callback_data=f'Задать_ключ_{token_id}'),
         InlineKeyboardButton(text='Задать категорию', callback_data=f'Задать_категорию_{token_id}')],
        [InlineKeyboardButton(text='Задать скидку', callback_data=f'Задать_скидку_{token_id}')],
        [InlineKeyboardButton(text='Переименовать токен', callback_data=f'Переименовать_токен_{token_id}')],
        [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
    ])

    return keyboard


async def main_menu(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text='Личный кабинет', callback_data='Личный_кабинет')],
        [InlineKeyboardButton(text='Информация', callback_data='Информация')]
    ]

    if user_id == 674796107:
        buttons.append([InlineKeyboardButton(text='Админка', callback_data='Админка')])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def list_to_inline(lvl: int, categories: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    buttons = []
    for category, id_ in categories:
        buttons.append([InlineKeyboardButton(text=category, callback_data=f'lvl{lvl}_{id_}')])
    buttons.append([InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
