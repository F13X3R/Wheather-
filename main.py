import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import json
import csv
import os

# Локализация интерфейса
TEXTS = {
    "Русский": {
        "city_prompt": "Укажите город:",
        "fetch_button": "Загрузить погоду",
        "title": "Текущая погода в",
        "desc": "Описание",
        "temp": "Темп-ра",
        "wind": "Скорость ветра",
        "hum": "Влажн.",
        "cloud": "Облачность",
        "fail_code": "Не удалось получить погоду. Код:",
        "fail_request": "Ошибка подключения: "
    },
    "English": {
        "city_prompt": "Type city name:",
        "fetch_button": "Load Weather",
        "title": "Weather for",
        "desc": "Condition",
        "temp": "Temperature",
        "wind": "Wind",
        "hum": "Humidity",
        "cloud": "Cloudiness",
        "fail_code": "Failed to retrieve data. Code:",
        "fail_request": "Connection error: "
    }
}

lang_choice = "Русский"
save_dir = r"D:\Курсовая работа"

def request_weather(city):
    link = f"https://wttr.in/{city}?format=%C|%t|%w|%h|%c&m"
    try:
        r = requests.get(link)
        if r.status_code == 200:
            parts = r.text.strip().split("|")
            if len(parts) == 5:
                keys = ["desc", "temp", "wind", "hum", "cloud"]
                return dict(zip(keys, parts))
            else:
                return None
        else:
            return f"{TEXTS[lang_choice]['fail_code']} {r.status_code}"
    except Exception as e:
        return f"{TEXTS[lang_choice]['fail_request']}{e}"

def show_weather_info():
    city = input_field.get().strip()
    if not city:
        display.delete(1.0, tk.END)
        display.insert(tk.END, "⚠️ Город не указан.")
        return

    result = request_weather(city)
    display.delete(1.0, tk.END)

    if isinstance(result, dict):
        text_lines = [
            f"{TEXTS[lang_choice]['title']} {city}",
            f"{TEXTS[lang_choice]['desc']}: {result['desc']}",
            f"{TEXTS[lang_choice]['temp']}: {result['temp']}",
            f"{TEXTS[lang_choice]['wind']}: {result['wind']}",
            f"{TEXTS[lang_choice]['hum']}: {result['hum']}",
            f"{TEXTS[lang_choice]['cloud']}: {result['cloud']}"
        ]
        output = "\n".join(text_lines)
        display.insert(tk.END, output)
        save_to_files(city, result)
    else:
        display.insert(tk.END, result)

def save_to_files(city, data):
    os.makedirs(save_dir, exist_ok=True)

    # Добавим название города
    record = {"Город": city}
    record.update({TEXTS[lang_choice][k]: v for k, v in data.items()})

    # JSON
    json_path = os.path.join(save_dir, "weather_data.json")
    if os.path.exists(json_path):
        with open(json_path, encoding="utf-8") as jf:
            content = json.load(jf)
    else:
        content = []

    content.append(record)
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(content, jf, ensure_ascii=False, indent=2)

    # CSV
    csv_path = os.path.join(save_dir, "weather_data.csv")
    header = list(record.keys())
    write_header = not os.path.exists(csv_path)
    with open(csv_path, "a", encoding="utf-8", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=header)
        if write_header:
            writer.writeheader()
        writer.writerow(record)

def update_language(selected):
    global lang_choice
    lang_choice = selected
    label_city.config(text=TEXTS[selected]["city_prompt"])
    fetch_btn.config(text=TEXTS[selected]["fetch_button"])

# GUI
app = tk.Tk()
app.title("Погодное приложение / Weather App")
app.geometry("400x400")

lang_frame = tk.Frame(app)
lang_frame.pack(pady=5)

tk.Label(lang_frame, text="Язык / Language:").pack(side=tk.LEFT, padx=5)
lang_var = tk.StringVar(value=lang_choice)
lang_menu = tk.OptionMenu(lang_frame, lang_var, *TEXTS.keys(), command=update_language)
lang_menu.pack(side=tk.LEFT)

label_city = tk.Label(app, text=TEXTS[lang_choice]["city_prompt"])
label_city.pack()
input_field = tk.Entry(app, width=30)
input_field.pack(pady=5)

fetch_btn = tk.Button(app, text=TEXTS[lang_choice]["fetch_button"], command=show_weather_info)
fetch_btn.pack()

display = scrolledtext.ScrolledText(app, wrap=tk.WORD, height=12)
display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

app.mainloop()
