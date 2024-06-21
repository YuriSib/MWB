import asyncio

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# import sys
# sys.path.append('../')

from config import BOT_TOKEN
import keyboards as kb
import bot_utilits as ut
from DB import sqlite_comands as sql
from parser.scrapper import wb_scrapper

router = Router()
bot = Bot(BOT_TOKEN)


@router.message(F.text == '/start')
async def step1(message: Message):
    if await sql.check_user(message.from_user.id):
        await message.answer('Выберите подходящий пункт:', reply_markup=kb.main_menu)
    else:
        await message.answer('Вам необходимо загерестрироваться:', reply_markup=kb.registration)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Главное_меню'))
async def personal_cabinet(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Выберите подходящий пункт:',
                           reply_markup=kb.cabinet_keyboard(callback.from_user.id))


class UserName(StatesGroup):
    name = State()


@router.callback_query(lambda callback_query: callback_query.data.startswith('Регистрация'))
async def personal_cabinet(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserName.name)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.answer(f'Ваше имя')
    await bot.send_message(chat_id=callback.from_user.id, text='Введите ваше имя:', reply_markup=kb.back_to_menu)


@router.message(UserName.name)
async def save_name(callback: CallbackQuery, state: FSMContext):
    await state.update_data(name=callback.text)
    name = callback.text

    print("Пользователь зарегестрировался!", callback.from_user.id, callback.chat.full_name)
    await sql.add_user(name, callback.from_user.id)
    await callback.bot.send_message(chat_id=callback.chat.id, text=f'{name}, вы успешно зарегестрировались!',
                                    reply_markup=kb.main_menu)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Личный_кабинет'))
async def personal_cabinet(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Выберите подходящий пункт:',
                           reply_markup=kb.cabinet_keyboard(callback.from_user.id))


@router.callback_query(lambda callback_query: callback_query.data.startswith('Мои_токены'))
async def tokens(callback: CallbackQuery, bot):
    """Тут будет функция, которая направит запрос в БД и вернет список токенов пользователя и срок их действия"""
    keys_data = await sql.get_token(callback.from_user.id)

    day_list = []
    for key in keys_data:
        q_days = await ut.subs_calculation(date=key[5], q_day=int(key[6]))
        if type(q_days) is int:
            day_list.append(q_days)
        else:
            await sql.delete_token(key[0])

    # 5 дней: 2 токена, 8 дней: 2 токена
    # tokens = {5: 2, 8: 2}
    tokens = {}
    if day_list:
        for q_day in day_list:
            if q_day in tokens:
                tokens[q_day] = int(tokens[q_day]) + 1
            else:
                tokens[q_day] = 1

        to_text = [f'{q_tokens} токен(а) сроком действия {day} дней' for day, q_tokens in tokens.items()]
        text = f'У вас осталось {", ".join(to_text)}. \nВыберите токен, который вы хотели бы настроить.'
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)

        token_list = await sql.get_token(callback.from_user.id)
        tokens_dict = {}
        no_name_num = 0
        for token_ in token_list:
            if token_[1]:
                tokens_dict[token_[0]] = token_[1]
            else:
                no_name_num += 1
                tokens_dict[token_[0]] = f'Безымянный {no_name_num}'

        await bot.send_message(chat_id=callback.from_user.id, text=text,
                               reply_markup=await kb.token_keyboard(tokens_dict))
    else:
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=callback.from_user.id,
                               text='В данный момент у вас нет токенов. Нажмите, приобретите один или несколько.',
                               reply_markup=kb.cabinet_keyboard(callback.from_user.id))


@router.callback_query(lambda callback_query: callback_query.data.startswith('Купить_токены'))
async def menu(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Купите свежие токены!', reply_markup=kb.pay_tokens)


class PayInfo(StatesGroup):
    photo = State()
    pay_option = State()


@router.callback_query(lambda callback_query: callback_query.data.startswith('оплатить_'))
async def waiting_to_pay(callback: CallbackQuery, state: FSMContext):
    pay_option = {
        'оплатить_1_на_7': (1, 7, 30), 'оплатить_3_на_7': (3, 7, 60),
        'оплатить_1_на_14': (1, 14, 50), 'оплатить_3_на_14': (3, 14, 100),
        'оплатить_1_на_30': (1, 30, 80), 'оплатить_3_на_30': (3, 30, 160),
    }
    token_params = pay_option[callback.data]
    q_t, q_d, price = token_params[0], token_params[1], token_params[2]
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'Оплатите {token_params[2]}р. в течении 10 мин. и перешлите '
                                f'Вы выбрали {q_t} токен(ов) на {q_d} дней. \n'
                                f'Оплатите {price} рублей за подписку и пришлите скриншот чека, '
                                f'после чего вам станут доступны преобретенные токены.')
    await state.set_state(PayInfo.photo)
    await state.update_data(pay_option=token_params)


@router.message(PayInfo.photo)
async def get_check(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo)
    photo_id = message.photo[2].file_id

    data = await state.get_data()
    token_params = data['pay_option']
    q_t, q_d, price = token_params[0], token_params[1], token_params[2]

    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Вы оплатили {q_t} токен(ов) на {q_d} дней!',
                           reply_markup=kb.pay_tokens)

    for i in range(1, token_params[0] + 1):
        await sql.add_token(message.from_user.id, token_params[1])

    for i in range(3):
        await bot.send_message(chat_id=674796107, text=f'Пользователь оплатил {price}р.!')
        await asyncio.sleep(1)
    await bot.send_photo(chat_id=674796107, photo=photo_id)


@router.callback_query(lambda callback_query: callback_query.data.startswith('токен_'))
async def menu(callback: CallbackQuery, bot):
    token_id = int(callback.data.replace('токен_', ''))
    token_data = await sql.get_token(token_id)

    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id,
                           text=f'Вы выбрали токен {token_data[0]}. Что вы хотите с ним сделать?:',
                           reply_markup=await kb.key_editor(token_id))


class KeyInfo(StatesGroup):
    keyword = State()
    token_id = State()
    token_name = State()
    discount = State()


@router.callback_query(lambda callback_query: callback_query.data.startswith('Задать_ключ_'))
async def keyword_input(callback: CallbackQuery, state: FSMContext):
    token_id = int(callback.data.replace('Задать_ключ_', ''))

    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Введите ключевое слово или фразу для поиска:',
                           reply_markup=kb.back_to_menu)

    await state.update_data(token_id=token_id)
    await state.set_state(KeyInfo.keyword)


@router.message(KeyInfo.keyword)
async def keyword_edit(message: Message, state: FSMContext):
    await state.update_data(keyword=message.text)

    data = await state.get_data()
    token_id = data['token_id']
    await sql.update_key_word_link(token_id, word=message.text)

    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Ваше новое ключевое слова для этого токена: \n{message.text}.',
                           reply_markup=await kb.key_editor(token_id))


@router.callback_query(lambda callback_query: callback_query.data.startswith('Переименовать_токен_'))
async def rename_token(callback: CallbackQuery, state: FSMContext):
    token_id = int(callback.data.replace('Переименовать_токен_', ''))

    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Введите новое название токена (не более 30 символов):')

    await state.update_data(token_id=token_id)
    await state.set_state(KeyInfo.token_name)


@router.message(KeyInfo.token_name)
async def keyword_edit(message: Message, state: FSMContext):
    await state.update_data(token_name=message.text)

    data = await state.get_data()
    token_id = data['token_id']

    await sql.update_token_name(token_id, message.text)

    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Ваше новое название для этого токена: \n{message.text}.',
                           reply_markup=await kb.key_editor(token_id))


@router.callback_query(lambda callback_query: callback_query.data.startswith('Задать_скидку_'))
async def rename_token(callback: CallbackQuery, state: FSMContext):
    token_id = int(callback.data.replace('Задать_скидку_', ''))

    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Введите процент скидки числом, без дополнительных знаков:')

    await state.update_data(token_id=token_id)
    await state.set_state(KeyInfo.discount)


@router.message(KeyInfo.discount)
async def keyword_edit(message: Message, state: FSMContext):
    await state.update_data(keyword=message.text)

    data = await state.get_data()
    token_id = data['token_id']

    await sql.update_discount(token_id, message.text)
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Ваша новая скидка для этого токена - {message.text}%',
                           reply_markup=await kb.key_editor(token_id))


@router.callback_query(lambda callback_query: callback_query.data.startswith('Категории'))
async def menu(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Выберите подходящий пункт:', reply_markup=kb.category)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Ввод_категории'))
async def menu(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Список категорий', reply_markup=kb.main_menu)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Запустить_мониторинг'))
async def menu(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)

    await sql.update_parsing_status(callback.from_user.id, True)
    lst_keyword = await sql.get_list_keyword(callback.from_user.id)
    await bot.send_message(chat_id=callback.from_user.id, text='Мониторинг запущен',
                           reply_markup=kb.cabinet_keyboard(callback.from_user.id))
    await wb_scrapper(lst_keyword, callback.from_user.id)
