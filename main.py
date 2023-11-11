# pip install aiogram python-decouple
#aiogram == 3.1.1

import os
import asyncio
import json

from datetime import datetime, timedelta
from random import choice, randint
from decouple import config

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder


API_TOKEN = config('TELEGRAM_API_TOKEN')
ADMIN_ID = config('TELEGRAM_ADMIN_ID')

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

list_courses = ["Python", "Java", "C++", "C#", "JavaScript", "PHP", "Ruby", "Go", "Swift", "Kotlin", "Rust", "Scala", "Haskell", "Perl", "Erlang", "R", "Dart", "TypeScript", "Lua", "Julia", "C", "Objective-C", "Visual Basic", "Assembly", "Delphi", "PowerShell", "SQL", "Groovy", "Clojure", "F#", "Racket", "Bash", "Lisp", "Pascal", "Fortran", "Ada", "Prolog", "Scheme", "COBOL", "ABAP", "Scratch", "Logo", "PL/SQL", "Transact-SQL", "Apex", "LabVIEW", "D", "Awk", "Dylan", "Elixir", "Forth", "Hack", "J", "Julia", "Korn", "Ladder", "LiveCode", "M", "Maple", "ML", "Nim", "OpenEdge", "OpenSCAD", "PL/I", "PostScript", "Q", "RPG", "SAS", "Smalltalk", "SPARK", "Tcl", "Verilog", "VHDL", "XQuery", "Z shell", "ZPL"]

def save_user(data, from_user):
    if not os.path.exists('users'):
        os.mkdir('users')    
    with open(f'users/{from_user.id}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    




class MenuState(StatesGroup):
    main_menu = State()

class RegiserState(StatesGroup):
    first_name = State()
    last_name = State()
    age = State()
    phone_number = State()
    photo = State()
    language_course = State()
    confirm = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(RegiserState.first_name)
    await message.answer("Як вас звати?")
    
@dp.message(Command("help"), default_state)
async def cmd_help(message: types.Message):
    await message.answer("Я можу тобі допомогти, але не хочу")    


@dp.message(RegiserState.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    
    await state.set_state(RegiserState.last_name)
    await message.answer("А як ваше прізвище?")
    
@dp.message(RegiserState.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    
    await state.set_state(RegiserState.age)
    await message.answer("Ведіть дату народження в форматі <b><i>дд.мм.рррр</i></b>")

@dp.message(RegiserState.age)
async def process_age(message: types.Message, state: FSMContext):
    try:
        print(message.text)
        date = datetime.strptime(message.text, "%d.%m.%Y")
        print(date)
        if date > datetime.now()-timedelta(days=365*5):
            await message.answer("Ви занадто молоді, щоб бути студентом, спробуйте ще раз")
            raise Exception("Too young")
    except:
        await message.answer("Введіть дату народження в форматі <b><i>дд.мм.рррр</i></b>")
        return
    
    await state.update_data(date_age=message.text)
    
    await state.set_state(RegiserState.phone_number)
    markup = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="Відправити номер телефону", request_contact=True)]
    ])
    
    await message.answer("Відправте номер телефону", reply_markup=markup)
    
@dp.message(RegiserState.phone_number, F.contact)
async def process_phone_number(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.contact.phone_number)
    
    await state.set_state(RegiserState.photo)
    await message.answer("Відправте фото для профілю (портрет)")
    
@dp.message(RegiserState.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    
    await state.set_state(RegiserState.language_course)
    
    
    builder = InlineKeyboardBuilder()
    for course in list_courses:
        builder.row(
            types.InlineKeyboardButton(text=course, callback_data=course)
        )
    
    
    await message.answer("Виберіть курс, на який хочете записатися", reply_markup=builder.as_markup())


@dp.callback_query(F.data.in_(list_courses),RegiserState.language_course)
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(language_course=callback_query.data)
    
    await state.set_state(RegiserState.confirm)
    
    data = await state.get_data()
    text = "Перевірте введені дані:\n"\
        f"Ім'я: {data['name']}\n"\
        f"Прізвище: {data['last_name']}\n"\
        f"Дата народження: {data['date_age']}\n"\
        f"Номер телефону: {data['phone_number']}\n"\
        f"Курс: {data['language_course']}\n"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Підтвердити", callback_data="confirm"),
        types.InlineKeyboardButton(text="Відмінити", callback_data="cancel")
    )
    
    await callback_query.message.answer_photo(data['photo'], caption=text, reply_markup=builder.as_markup())

@dp.callback_query(RegiserState.confirm, F.data == "confirm")
async def process_callback_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    save_user(data, callback_query.from_user)
    
    await state.clear()
    
    await callback_query.message.answer("Ви успішно зареєструвались\n Дякуємо за реєстрацію")


async def main():
    print("Starting bot...")
    print("Bot username: @{}".format((await bot.me())))
    await dp.start_polling(bot)

asyncio.run(main())