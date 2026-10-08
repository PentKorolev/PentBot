import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Booking(StatesGroup):
    name = State()
    date = State()
    time = State()
    guests = State()
    phone = State()

start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🍽 Забронировать столик")]],
    resize_keyboard=True
)
cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Здравствуйте! 👋\n"
        "Я помогу забронировать столик в нашем заведении.\n\n"
        "Нажмите кнопку ниже, чтобы оставить заявку.",
        reply_markup=start_kb
    )

@dp.message(F.text == "🍽 Забронировать столик")
async def start_booking(message: types.Message, state: FSMContext):
    await state.set_state(Booking.name)
    await message.answer("Как к вам обращаться?", reply_markup=cancel_kb)

@dp.message(F.text == "❌ Отмена")
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Бронь отменена. Если захотите — начните заново.", reply_markup=start_kb)

@dp.message(Booking.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Booking.date)
    await message.answer("На какую дату? (например, 15 июня)")

@dp.message(Booking.date)
async def process_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(Booking.time)
    await message.answer("На какое время? (например, 19:00)")

@dp.message(Booking.time)
async def process_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(Booking.guests)
    await message.answer("Сколько гостей?")

@dp.message(Booking.guests)
async def process_guests(message: types.Message, state: FSMContext):
    await state.update_data(guests=message.text)
    await state.set_state(Booking.phone)
    await message.answer("Ваш телефон для подтверждения?")

@dp.message(Booking.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    await state.clear()
    booking_text = (
        "🍽 НОВАЯ БРОНЬ СТОЛИКА\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📅 Дата: {data['date']}\n"
        f"🕐 Время: {data['time']}\n"
        f"👥 Гостей: {data['guests']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"💬 Telegram: @{message.from_user.username or 'нет'}"
    )
    await bot.send_message(ADMIN_ID, booking_text)
    await message.answer("Спасибо! ✅\nЗаявка принята.", reply_markup=start_kb)
    
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
