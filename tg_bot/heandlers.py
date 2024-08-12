import asyncio

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import sys
sys.path.append('../')

from config import BOT_TOKEN
import keyboards as kb
import bot_utilits as ut
from DB import sqlite_comands as sql
from parser.scrapper import wb_scrapper
from parser.utilits import get_categories
from logger import logger as log

router = Router()
bot = Bot(BOT_TOKEN)

MONITORING_FLAG = False


@router.message(F.text == '/start')
async def step1(message: Message):
    if await sql.check_user(message.from_user.id):
        await message.answer('Выберите подходящий пункт:', reply_markup=await kb.main_menu(message.from_user.id))
    else:
        await message.answer('Вам необходимо загерестрироваться:', reply_markup=kb.registration)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Главное_меню'))
async def personal_cabinet(callback: CallbackQuery, bot):
    print(callback.message.message_id)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Выберите подходящий пункт:',
                           reply_markup=await kb.main_menu(callback.from_user.id))


@router.callback_query(lambda callback_query: callback_query.data.startswith('Админка'))
async def admin_menu(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Выберите подходящий пункт:',
                           reply_markup=kb.admin_menu)


class UserName(StatesGroup):
    name = State()


@router.callback_query(lambda callback_query: callback_query.data.startswith('Регистрация'))
async def personal_cabinet(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserName.name)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.answer(f'Ваше имя')
    await bot.send_message(chat_id=callback.from_user.id, text='Введите ваше имя:', reply_markup=kb.back_to_menu)
    log.user_logger.info(f"Новый пользователь зареган! {callback.from_user.id}: {callback.from_user.username}")


@router.message(UserName.name)
async def save_name(callback: CallbackQuery, state: FSMContext):
    await state.update_data(name=callback.text)
    name = callback.text

    print("Пользователь зарегестрировался!", callback.from_user.id, callback.chat.full_name)
    await sql.add_user(name, callback.from_user.id)
    await callback.bot.send_message(chat_id=callback.chat.id, text=f'{name}, вы успешно зарегестрировались!',
                                    reply_markup=await kb.main_menu(callback.from_user.id))


@router.callback_query(lambda callback_query: callback_query.data.startswith('Личный_кабинет'))
async def personal_cabinet(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Выберите подходящий пункт:',
                           reply_markup=kb.personal_cabinet)


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
                               reply_markup=kb.personal_cabinet)


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
        await sql.add_token(message.from_user.id, token_params[1], username=message.from_user.username)

    for i in range(3):
        await bot.send_message(chat_id=674796107, text=f'Пользователь оплатил {price}р.!')
        await asyncio.sleep(1)
    log.info(f"Пользователь {message.from_user.id}: {message.from_user.username} купил токен!")
    await bot.send_photo(chat_id=674796107, photo=photo_id)


@router.callback_query(lambda callback_query: callback_query.data.startswith('токен_'))
async def menu(callback: CallbackQuery, bot):
    token_id = int(callback.data.replace('токен_', ''))
    token_data = await sql.get_a_token(token_id)

    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    print(token_data)
    if token_data:
        await bot.send_message(chat_id=callback.from_user.id,
                               text=f'Вы выбрали токен {token_data[0][1]}. \n'
                                    f'Категория - {token_data[0][2]}, Ключевое слово - {token_data[0][3]}, '
                                    f'снижение цены - {token_data[0][4]}%'
                                    f'\nЧто вы хотите с ним сделать?:',
                               reply_markup=await kb.key_editor(token_id))
    else:
        await bot.send_message(chat_id=callback.from_user.id,
                               text=f'Вы выбрали безымянный токен. Что вы хотите с ним сделать?:',
                               reply_markup=await kb.key_editor(token_id))


class KeyInfo(StatesGroup):
    keyword = State()
    token_id = State()
    token_name = State()
    discount = State()
    catalog_tree = State()
    id_dict = State()
    lvl_1_id, lvl_2_id, lvl_3_id, lvl_4_id, lvl_5_id = State(), State(), State(), State(), State()


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
    await sql.update_key(token_id, word=message.text)

    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Ваше новое ключевое слова для этого токена: \n{message.text}.',
                           reply_markup=await kb.key_editor(token_id))
    await sql.update_token_name(token_id=token_id, name='Ключ - '+message.text)
    log.info(f"Пользователь {message.from_user.id}: {message.from_user.username} задал новый ключ!")


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
async def discount(callback: CallbackQuery, state: FSMContext):
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


@router.callback_query(lambda callback_query: callback_query.data.startswith('Задать_категорию_'))
async def choice_category(callback: CallbackQuery, state: FSMContext):
    token_id = int(callback.data.replace('Задать_категорию_', ''))
    catalog_tree, id_dict = await get_categories()

    await state.update_data(token_id=token_id)
    await state.update_data(catalog_tree=catalog_tree)
    await state.update_data(id_dict=id_dict)

    categories = [id_ for id_ in catalog_tree]
    category_id = [(id_dict[id_], id_) for id_ in categories]

    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Выберите нужную категорию из списка',
                           reply_markup=await kb.list_to_inline(1, category_id))


@router.callback_query(lambda callback_query: callback_query.data.startswith('lvl1_'))
async def lvl_1(callback: CallbackQuery, state: FSMContext):
    await ut.choice_category_lvl(lvl=1, callback=callback, state=state, bot=bot)


@router.callback_query(lambda callback_query: callback_query.data.startswith('lvl2_'))
async def lvl_2(callback: CallbackQuery, state: FSMContext):
    await ut.choice_category_lvl(lvl=2, callback=callback, state=state, bot=bot)


@router.callback_query(lambda callback_query: callback_query.data.startswith('lvl3_'))
async def lvl_3(callback: CallbackQuery, state: FSMContext):
    await ut.choice_category_lvl(lvl=3, callback=callback, state=state, bot=bot)


@router.callback_query(lambda callback_query: callback_query.data.startswith('lvl4_'))
async def lvl_3(callback: CallbackQuery, state: FSMContext):
    await ut.choice_category_lvl(lvl=4, callback=callback, state=state, bot=bot)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Запустить_мониторинг'))
async def start_monitoring(callback: CallbackQuery, bot):
    await sql.update_parsing_status(True)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Мониторинг запущен',
                           reply_markup=kb.admin_menu)

    while True:
        token_list = await sql.get_tokens()
        for token in token_list:
            category, keyword, discount_proc, user_id = token[2], token[3], token[4], token[7]

            if not discount_proc:
                continue

            if keyword != '0':
                await wb_scrapper(user_id, discount_proc, keyword=keyword)
                log.debug(f'Запустил wb_scrapper для ключа {keyword}, User - {user_id}')
            else:
                await wb_scrapper(user_id, discount_proc, category=category)
                log.debug(f'Запустил wb_scrapper для категории {category}, User - {user_id}')


@router.callback_query(lambda callback_query: callback_query.data.startswith('Остановить_мониторинг'))
async def stop_monitoring(callback: CallbackQuery, bot):
    await sql.update_parsing_status(False)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Мониторинг остановлен',
                           reply_markup=kb.admin_menu)
