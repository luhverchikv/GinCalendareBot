from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram_calendar import simple_cal_callback, SimpleCalendar # pip install aiogram-calendar
import datetime
from config import API_TOKEN

# API_TOKEN = '' uncomment and insert your telegram bot API key here


# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# star keybord ('Сегодня', 'Выбрать Дату', 'Помощь')
start_kb = ReplyKeyboardMarkup(resize_keyboard=True,)
start_kb.row('Сегодня', 'Выбрать Дату', 'Помощь')


@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    await message.reply('Введите дату и получите новую дату через 126 календарных дней',
                        reply_markup=start_kb)


@dp.message_handler(Text(equals=['Выбрать Дату'], ignore_case=True))
async def nav_cal_handler(message: Message):
    await message.answer("Выберите дату: ", reply_markup=await SimpleCalendar().start_calendar())


# simple calendar usage
@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    future = date + datetime.timedelta(days=125)
    if selected:
        await callback_query.message.answer(
            f'Вы выбрали: {date.strftime("%d.%m.%Y")}\nЧерез 126 дней: {future.strftime("%d.%m.%Y")}',
            reply_markup=start_kb
        )


@dp.message_handler(Text(equals=['Сегодня'], ignore_case=True))
async def simple_cal_handler(message: Message):
    now = datetime.datetime.now()
    future = now + datetime.timedelta(days=125) # на один день меньше, так как счет не с 0, а с 1.
    future_date = future.strftime('%d.%m.%Y')
    await message.answer(f"Сегодня: {now.strftime('%d.%m.%Y')}\nЧерез 126 дней: {future_date}")


@dp.message_handler(Text(equals=['Помощь'], ignore_case=True))
async def simple_cal_handler(message: Message):
    await message.answer(f'Лучше звоните <a href="https://t.me/ImAntonbatura">Антону</a>',
                             parse_mode=ParseMode.HTML)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
