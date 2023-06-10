from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound
from aiogram_calendar import simple_cal_callback, SimpleCalendar  # pip install aiogram-calendar
from contextlib import suppress
import datetime
from config import API_TOKEN
from loguru import logger
import asyncio

# API_TOKEN = '' uncomment and insert your telegram bot API key here


# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logger.add('ihfo.log', format="{time} {level} {message}", level="INFO",
           rotation="1 week", compression="zip")

# star keybord ('Сегодня', 'Выбрать Дату', 'Помощь')
start_kb = ReplyKeyboardMarkup(resize_keyboard=True, )
start_kb.row('Сегодня', 'Выбрать Дату', 'Помощь')


async def delete_message(message: types.Message, seconds: int = 0):
    await asyncio.sleep(seconds)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    logger.info(f'Пользователь {message.from_user.id} начал взаимодействие')
    await message.reply('Введите дату и получите новую дату через 126 календарных дней',
                        reply_markup=start_kb)


@dp.message_handler(Text(equals=['Выбрать Дату'], ignore_case=True))
async def nav_cal_handler(message: Message):
    logger.info(f'Пользователь {message.from_user.id} нажал "Календарь"')
    await message.answer("Выберите дату: ", reply_markup=await SimpleCalendar().start_calendar())
    asyncio.create_task(delete_message(message, 5))


# simple calendar usage
@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    future = date + datetime.timedelta(days=125)
    if selected:
        answer = await callback_query.message.answer(f'Вы выбрали: {date.strftime("%d.%m.%Y")}\n'
                                                     f'Через 126 дней: {future.strftime("%d.%m.%Y")}')
        asyncio.create_task(delete_message(callback_query.message, 5))
        asyncio.create_task(delete_message(answer, 10))


@dp.message_handler(Text(equals=['Сегодня'], ignore_case=True))
async def simple_cal_handler(message: Message):
    logger.info(f'Пользователь {message.from_user.id} нажал "Сегодня"')
    now = datetime.datetime.now()
    future = now + datetime.timedelta(days=125)  # на один день меньше, так как счет не с 0, а с 1.
    future_date = future.strftime('%d.%m.%Y')
    answer = await message.answer(f"Сегодня: {now.strftime('%d.%m.%Y')}\nЧерез 126 дней: {future_date}")
    asyncio.create_task(delete_message(message, 5))
    asyncio.create_task(delete_message(answer, 10))


@dp.message_handler(Text(equals=['Помощь'], ignore_case=True))
async def simple_cal_handler(message: Message):
    logger.info(f'Пользователь {message.from_user.id} нажал "Помощь"')
    answer = await message.answer(f'Мой <a href="https://t.me/luhverchik">номер</a>',
                                  parse_mode=ParseMode.HTML)
    asyncio.create_task(delete_message(message, 5))
    asyncio.create_task(delete_message(answer, 10))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
