from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


registration = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Зарегистрироваться', callback_data='Регистрация'),
     InlineKeyboardButton(text='Справка', callback_data='Справка')],
    [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
])

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Личный кабинет', callback_data='Личный_кабинет')],
    [InlineKeyboardButton(text='Задать ключи', callback_data='Ключи'),
     InlineKeyboardButton(text='Задать категории', callback_data='Категории')]
])

personal_cabinet = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Мои токены', callback_data='Мои_токены'),
     InlineKeyboardButton(text='Купить токены', callback_data='Купить_токены')],
    [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
])

keys = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ввод ключа', callback_data='Ввод_ключа')],
    [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
])

pay_tokens = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1 токен на 7 дней', callback_data='оплатить_1_на_7'),
     InlineKeyboardButton(text='3 токена на 7 дней', callback_data='оплатить_3_на_7')],
    [InlineKeyboardButton(text='1 токен на 14 дней', callback_data='оплатить_1_на_14'),
     InlineKeyboardButton(text='3 токена на 14 дней', callback_data='оплатить_3_на_14')],
    [InlineKeyboardButton(text='1 токен на 30 дней', callback_data='оплатить_1_на_30'),
     InlineKeyboardButton(text='3 токена на 30 дней', callback_data='оплатить_3_на_30')],
    [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
])

setting_token = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Переименовать токен', callback_data='Переименовать')],
    [InlineKeyboardButton(text='Задать ключ мониторинга', callback_data='Задать_ключ'),
     InlineKeyboardButton(text='Задать категорию мониторинга', callback_data='Задать_категорию')],
    [InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')]
])

category = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Введите номер категории из списка', callback_data='Ввод_категории')],
    [InlineKeyboardButton(text='На категорию вверх', callback_data='На_категорию_вверх')],
    [InlineKeyboardButton(text='Выбрать категорию', callback_data='Выбрать категорию')],
])

percent = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Укажите процент', callback_data='Укажите_процент')]
])


async def token_keyboard(tokens: dict) -> InlineKeyboardMarkup:
    row = []
    for id_, name in tokens.items():
        row.append([InlineKeyboardButton(text=name, callback_data=f'токен_{id_}')])
    row.append([InlineKeyboardButton(text='Назад в главное меню', callback_data='Главное_меню')])

    return InlineKeyboardMarkup(inline_keyboard=row)
