from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import BOT_TOKEN
import keyboards as kb
from DB import sqlite_comands as sql

router = Router()
bot = Bot(BOT_TOKEN)


@router.message(F.text == '/start')
async def step1(message: Message):
    if await sql.check_user(message.from_user.id):
        await message.answer('Выберите подходящий пункт:', reply_markup=kb.main_menu)
    else:
        await message.answer('Вам необходимо загерестрироваться:', reply_markup=kb.registration)


class UserName(StatesGroup):
    name = State()


@router.callback_query(lambda callback_query: callback_query.data.startswith('Регистрация'))
async def personal_cabinet(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserName.name)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.answer(f'Ваше имя')
    await bot.send_message(chat_id=callback.from_user.id, text='Введите ваше имя:')


@router.message(UserName.name)
async def save_name(callback: CallbackQuery, state: FSMContext):
    await state.update_data(name=callback.text)
    name = callback.text

    print("Пользователь зарегестрировался!", callback.from_user.id, callback.chat.full_name)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await sql.add_user(name, callback.from_user.id)
    await callback.bot.send_message(chat_id=callback.chat.id, text=f'{name}, вы успешно авторизовались!',
                                    reply_markup=kb.main_menu)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Личный_кабинет'))
async def personal_cabinet(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Выберите подходящий пункт:',
                           reply_markup=kb.personal_cabinet)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Мои_токены'))
async def tokens(callback: CallbackQuery, bot):
    """Тут будет функция, которая направит запрос в БД и вернет список токенов пользователя и срок их действия"""
    # 5 дней: 2 токена, 8 дней: 2 токена
    tokens = {5: 2, 8: 2}
    to_text = [f'{q_tokens} токен(а) сроком действия по {day} дней' for day, q_tokens in tokens.items()]
    text = f'У вас осталось {", ".join(to_text)}.'
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text=text, reply_markup=kb.main_menu)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Купить_токены'))
async def menu(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Купите свежие токены!', reply_markup=kb.main_menu)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Ключи'))
async def menu(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Выберите подходящий пункт:', reply_markup=kb.keys)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Категории'))
async def menu(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Выберите подходящий пункт:', reply_markup=kb.category)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Ввод_ключа'))
async def menu(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Введите ключ для поиска', reply_markup=kb.main_menu)


@router.callback_query(lambda callback_query: callback_query.data.startswith('Ввод_категории'))
async def menu(callback: CallbackQuery, bot):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Список категорий', reply_markup=kb.main_menu)
