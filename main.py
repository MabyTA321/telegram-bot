import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import requests
import os
API_KEY = "8f3f02db86f531f7507476d4836bf1b4"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},MD&appid={API_KEY}&units=metric"

    try:
        res = requests.get(url)
        data = res.json()

        print("API RESPONSE:", data)  # 👈 ВАЖНО

        if "main" not in data:
            return None

        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        condition = data["weather"][0]["main"]

        return temperature, humidity, pressure, wind, condition

    except:
        return None
    
    
    
    # Wehther Emoji
def get_weather_emoji(condition):
    if condition == "Clear":
        return "☀️"
    elif condition == "Clouds":
        return "☁️"
    elif condition == "Rain":
        return "🌧"
    elif condition == "Snow":
        return "❄️"
    elif condition == "Thunderstorm":
        return "⛈"
    else:
        return "🌡"

def fish_rating(score):
    # transformăm scorul 0–10 în 0–5
    fish = round(score / 2)

    return "🐟" * fish + "▫️" * (5 - fish)

def score_text(score, lang):
    if lang == "ro":
        if score >= 8:
            return "🔥 Excelent"
        elif score >= 5:
            return "👍 Bun"
        else:
            return "⚠️ Slab"
    else:
        if score >= 8:
            return "🔥 Отлично"
        elif score >= 5:
            return "👍 Хорошо"
        else:
            return "⚠️ Слабо"


def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},MD&appid={API_KEY}&units=metric"

    try:
        res = requests.get(url)
        data = res.json()

        if "list" not in data:
            return None

        return data["list"]

    except:
        return None


TOKEN = os.getenv("TOKEN")
user_period = {}

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ХРАНЕНИЕ ЯЗЫКА ---
user_lang = {}

districts = [
"Anenii Noi", "Basarabeasca", "Briceni", "Cahul", "Cantemir",
"Călărași", "Căușeni", "Cimișlia", "Criuleni", "Dondușeni",
"Drochia", "Dubăsari", "Edineț", "Fălești", "Florești",
"Glodeni", "Hîncești", "Ialoveni", "Leova", "Nisporeni",
"Ocnița", "Orhei", "Rezina", "Rîșcani", "Sîngerei",
"Soroca", "Strășeni", "Șoldănești", "Ștefan Vodă",
"Taraclia", "Telenești", "Ungheni"
]

user_state = {}

# --- КНОПКИ ЯЗЫКА ---
lang_builder = ReplyKeyboardBuilder()
lang_builder.button(text="🇷🇴 Română")
lang_builder.button(text="🇷🇺 Русский")
lang_builder.adjust(2)

lang_kb = lang_builder.as_markup(resize_keyboard=True)

# --- PERIOD RO ---
period_builder_ro = ReplyKeyboardBuilder()
period_builder_ro.button(text="Astăzi")
period_builder_ro.button(text="3 zile")
period_builder_ro.button(text="Săptămână")
period_builder_ro.adjust(1)

period_kb_ro = period_builder_ro.as_markup(resize_keyboard=True)

# --- PERIOD RU ---
period_builder_ru = ReplyKeyboardBuilder()
period_builder_ru.button(text="Сегодня")
period_builder_ru.button(text="3 дня")
period_builder_ru.button(text="Неделя")
period_builder_ru.adjust(1)

period_kb_ru = period_builder_ru.as_markup(resize_keyboard=True)

def get_district_kb(lang):
    builder = ReplyKeyboardBuilder()

    for d in districts:
        builder.button(text=d)

    # 👇 buton inapoi
    if lang == "ro":
        builder.button(text="⬅️ Înapoi")
    else:
        builder.button(text="⬅️ Назад")

    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)

# --- START ---
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Selectează limba / Выберите язык 👇",
        reply_markup=lang_kb
    )

# --- ОБРАБОТКА ---
@dp.message()
async def handle(message: Message):
    print("TEXT:", message.text)
    text = message.text
    user_id = message.from_user.id

    # --- BACK BUTTON ---
    if text in ["⬅️ Înapoi", "⬅️ Назад"]:
        lang = user_lang.get(user_id, "ru")

        # inapoi la perioada
        if user_state.get(user_id) == "choose_district":
            user_state[user_id] = "choose_period"

            if lang == "ro":
                await message.answer("Alege perioada 👇", reply_markup=period_kb_ro)
            else:
                await message.answer("Выбери период 👇", reply_markup=period_kb_ru)

        else:
            # inapoi la limba
            user_state[user_id] = "choose_lang"
            await message.answer(
                "Selectează limba / Выберите язык 👇",
                reply_markup=lang_kb
            )

        return

    # 🇷🇴 ROMANA
    if text == "🇷🇴 Română":
        user_lang[user_id] = "ro"
        print("LANG SET:", user_lang[user_id])
        await message.answer(
            "🤖 Acest bot te ajută să afli prognoza pescuitului 🎣\n\n"
            "📌 Instrucțiuni:\n"
            "1. Alegi localitatea\n"
            "2. Alegi perioada\n"
            "3. Primești prognoza\n\n"
            "Alege perioada 👇",
            reply_markup=period_kb_ro
        )

    # 🇷🇺 RUSSIAN
    elif text == "🇷🇺 Русский":
        user_lang[user_id] = "ru"
        await message.answer(
            "🤖 Этот бот помогает узнать прогноз клёва 🎣\n\n"
            "📌 Инструкция:\n"
            "1. Выбери населённый пункт\n"
            "2. Выбери период\n"
            "3. Получи прогноз\n\n"
            "Выбери период 👇",
            reply_markup=period_kb_ru
        )

    # --- ПЕРИОД ---
    elif text in ["Сегодня", "3 дня", "Неделя", "Astăzi", "3 zile", "Săptămână"]:
        user_state[user_id] = "choose_district"
        user_period[user_id] = text
        lang = user_lang.get(user_id, "ru")

        if lang == "ro":
            await message.answer("📍 Alege raionul:", reply_markup=get_district_kb(lang))
        else:
            await message.answer("📍 Выбери район:", reply_markup=get_district_kb(lang))
    elif user_state.get(user_id) == "choose_district" and text in districts:

        period = user_period.get(user_id, "Astăzi")
        lang = user_lang.get(user_id, "ru")
        district = text

    # ================= AZI =================
        if period in ["Astăzi", "Сегодня"]:
            data = get_weather(district)

            if data is None:
                await message.answer("❌ Nu am găsit date")
                return

            temperature, humidity, pressure, wind, condition = data

            emoji = get_weather_emoji(condition)

            condition_original = condition

            condition_map_ru = {
                "Clear": "Ясно",
                "Clouds": "Облачно",
                "Rain": "Дождь",
                "Snow": "Снег",
                "Thunderstorm": "Гроза"
            }

            condition_map_ro = {
                "Clear": "Senin",
                "Clouds": "Noros",
                "Rain": "Ploaie",
                "Snow": "Zăpadă",
                "Thunderstorm": "Furtună"
            }

            condition_ru = condition_map_ru.get(condition_original, condition_original)
            condition_ro = condition_map_ro.get(condition_original, condition_original)

            # SCOR
            score = 0

            if 1008 <= pressure <= 1022:
                score += 3
            elif pressure < 1000:
                score += 2

            if wind <= 4:
                score += 2
            elif wind <= 7:
                score += 1

            if 12 <= temperature <= 24:
                score += 3
            elif 5 <= temperature < 12 or 24 < temperature <= 30:
                score += 1

            if condition_original in ["Clouds", "Rain"]:
                score += 2
            elif condition_original == "Clear":
                score += 1

            score = min(score, 10)
            

            fish_bar = fish_rating(score)
            text_score = score_text(score, lang)

            # OUTPUT
            if lang == "ro":
                response = (
                    f"📍 <b>{district}</b>\n\n"
                    f"{emoji} <b>Stare:</b> {condition_ro}\n"
                    f"🌡 <b>Temperatura:</b> {temperature}°C\n"
                    f"💧 <b>Umiditate:</b> {humidity}%\n"
                    f"📈 <b>Presiune:</b> {pressure} hPa\n"
                    f"💨 <b>Vânt:</b> {wind} m/s\n\n"
                    f"🎣 <b>Scor pescuit:</b> {score}/10\n{fish_bar}\n{text_score}"
                )
            else:
                response = (
                    f"📍 <b>{district}</b>\n\n"
                    f"{emoji} <b>Состояние:</b> {condition_ru}\n"
                    f"🌡 <b>Температура:</b> {temperature}°C\n"
                    f"💧 <b>Влажность:</b> {humidity}%\n"
                    f"📈 <b>Давление:</b> {pressure} гПа\n"
                    f"💨 <b>Ветер:</b> {wind} м/с\n\n"
                    f"🎣 <b>Рейтинг клёва:</b> {score}/10\n{fish_bar}\n{text_score}"
                )

            await message.answer(response, parse_mode="HTML")

            await message.answer(
                "⬇️ Alege alt raion sau apasă Înapoi" if lang == "ro"
                else "⬇️ Выбери другой район или назад",
                reply_markup=get_district_kb(lang)
            )
        else:
            forecast = get_forecast(district)

            if forecast is None:
                await message.answer("❌ Nu am găsit prognoza")
                return

            from datetime import datetime

            days_data = {}

            for item in forecast:
                date = datetime.fromtimestamp(item["dt"]).strftime("%d.%m")

                if date not in days_data:
                    days_data[date] = item

            if period in ["3 zile", "3 дня"]:
                selected_days = list(days_data.values())[:3]
            else:
                selected_days = list(days_data.values())[:5]

            # 🔥 AICI TRIMITEM PE FIECARE ZI
            for item in selected_days:

                date = datetime.fromtimestamp(item["dt"]).strftime("%d.%m")

                temperature = item["main"]["temp"]
                humidity = item["main"]["humidity"]
                pressure = item["main"]["pressure"]
                wind = item["wind"]["speed"]
                condition = item["weather"][0]["main"]

                emoji = get_weather_emoji(condition)

                condition_original = condition

                condition_map_ru = {
                    "Clear": "Ясно",
                    "Clouds": "Облачно",
                    "Rain": "Дождь",
                    "Snow": "Снег",
                    "Thunderstorm": "Гроза"
                }

                condition_map_ro = {
                    "Clear": "Senin",
                    "Clouds": "Noros",
                    "Rain": "Ploaie",
                    "Snow": "Zăpadă",
                    "Thunderstorm": "Furtună"
                }

                condition_ru = condition_map_ru.get(condition_original, condition_original)
                condition_ro = condition_map_ro.get(condition_original, condition_original)

                score = 0

                if 1008 <= pressure <= 1022:
                    score += 3
                elif pressure < 1000:
                    score += 2

                if wind <= 4:
                    score += 2
                elif wind <= 7:
                    score += 1

                if 12 <= temperature <= 24:
                    score += 3
                elif 5 <= temperature < 12 or 24 < temperature <= 30:
                    score += 1

                if condition in ["Clouds", "Rain"]:
                    score += 2
                elif condition == "Clear":
                    score += 1

                score = min(score, 10)
                fish_bar = fish_rating(score)
                text_score = score_text(score)

                if lang == "ro":
                    response = (
                        f"📍 <b>{district}</b>\n"
                        f"📅 <b>{date}</b>\n\n"
                        f"{emoji} <b>Stare:</b> {condition_ro}\n"
                        f"🌡 <b>Temperatura:</b> {temperature}°C\n"
                        f"💧 <b>Umiditate:</b> {humidity}%\n"
                        f"📈 <b>Presiune:</b> {pressure} hPa\n"
                        f"💨 <b>Vânt:</b> {wind} m/s\n\n"
                        f"🎣 <b>Scor pescuit:</b> {score}/10\n{fish_bar}\n{text_score}"
                        )
                else:
                    response = (
                        f"📍 <b>{district}</b>\n"
                        f"📅 <b>{date}</b>\n\n"
                        f"{emoji} <b>Состояние:</b> {condition_ru}\n"
                        f"🌡 <b>Температура:</b> {temperature}°C\n"
                        f"💧 <b>Влажность:</b> {humidity}%\n"
                        f"📈 <b>Давление:</b> {pressure} гПа\n"
                        f"💨 <b>Ветер:</b> {wind} м/с\n\n"
                        f"🎣 <b>Рейтинг клёва:</b> {score}/10\n{fish_bar}\n{text_score}"
                    )

                await message.answer(response, parse_mode="HTML")


# --- ЗАПУСК ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())