import telebot
from telethon import TelegramClient
import asyncio
import os
import re
from collections import Counter
from datetime import datetime

API_TOKEN = '6911931516:AAHYBsAlbuYYicgn7YnDZkkEMlWsg1nH9ow'
api_id = '20422415'
api_hash = 'a0b33af22b30ce389e6705a0d3a98347'
phone = '+33 7 66 86 88 34'

bot = telebot.TeleBot(API_TOKEN)
client = TelegramClient('session_name', api_id, api_hash)

# Список названий для кнопок
button_labels = [
    "Phoenix", "Tucson", "Scottdale", "Chandler", "Brainburg",
    "SaintRose", "Mesa", "RedRock", "Yuma", "Surprise",
    "Prescott", "Glendale", "Kingman", "Winslow", "Payson",
    "Gilbert", "Show Low", "Casa-Grande", "Page", "Sun-City",
    "Queen-Creek", "Sedona", "Holiday", "Wednesday", "Yava",
    "Faraway", "BumbleBee", "Christmas", "Mirage", "Love"
]

# Функция для создания кнопок
def create_buttons():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=5)
    buttons = [telebot.types.KeyboardButton(text=label) for label in button_labels]
    markup.add(*buttons)
    return markup

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = create_buttons()
    bot.send_message(message.chat.id, "Выберите кнопку:", reply_markup=markup)

# Обработчик нажатий на кнопки
@bot.message_handler(func=lambda message: message.text in button_labels)
def handle_query(message):
    label = message.text
    number = button_labels.index(label) + 1  # Получение номера кнопки
    asyncio.run_coroutine_threadsafe(run_main_with_param(number, label, message.chat.id), asyncio.get_event_loop())
    bot.send_message(message.chat.id, f'Файл для параметра {number} ({label}) создан и обработан.')

# Асинхронная функция для выполнения основного скрипта
async def main(param, label, chat_id):
    await client.start(phone=phone)
    print("Клиент запущен")

    # Найти бота
    bot_entity = await client.get_entity('https://t.me/ARZMonitoring_bot')

    # Отправить команду /start
    await client.send_message(bot_entity, '/start')
    await asyncio.sleep(1)  # Задержка для ожидания ответа

    # Нажать кнопку "Меню Владельцев 👥"
    await client.send_message(bot_entity, 'Меню Владельцев 👥')
    await asyncio.sleep(1)

    # Нажать кнопку "По промежутку 🧩"
    await client.send_message(bot_entity, 'По промежутку 🧩')
    await asyncio.sleep(1)

    # Отправить строку с параметром
    await client.send_message(bot_entity, f'{param} 2 0-500')
    await asyncio.sleep(4)

    # Копировать следующие 7 сообщений от бота
    messages = []
    async for message in client.iter_messages(bot_entity, limit=7):
        messages.append(message.text)

    filename = f'{label}.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        for message in reversed(messages):  # Запись сообщений в правильном порядке
            f.write(message)

    print(f"Сообщения сохранены в файл {filename}")
    output_file = process_file(filename,label)  # Обработка файла функцией process_file
    await send_file(chat_id, output_file)

# Функция для обработки файла
def process_file(file_path,lable):
    # Прочитать файл и разделить его на строки
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Создать список только с именами и типами бизнеса
    names_and_types = []
    for line in lines:
        match = re.search(r'\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', line)
        if match:
            business_type = match.group(1).strip()
            num = match.group(2).strip()
            name = match.group(3).strip()
            names_and_types.append((name, business_type, num))
        else:
            print(f"Не удалось обработать строку: {line}")

    # Подсчитать количество повторений каждого имени без учёта типа бизнеса
    name_counts = Counter(name for name, _, _ in names_and_types)

    # Создать имя файла с текущей датой и временем
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"{lable}_{current_datetime}.html"

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('<!DOCTYPE html>\n')
        file.write('<html>\n')
        file.write('<head>\n')
        file.write('<title>BizCheck by monejey</title>\n')
        file.write('<link href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;700&display=swap" rel="stylesheet">\n')
        file.write('<style>\n')
        file.write('body { background-color: #2e2e2e; color: #f2f2f2; font-family: "Golos Text", Arial, sans-serif; }\n')
        file.write('.filters { margin-bottom: 5px; }\n')  # Reduced margin-bottom
        file.write('table { margin-top: 0; }\n')  # Ensure no top margin for the table
        file.write('table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 20px; border-radius: 10px; overflow: hidden; }\n')
        file.write('.header { font-size: 24px; font-weight: bold; margin-bottom: 10px; }\n')  # Added styles for header
        file.write('th, td { border: 1px solid #444; text-align: left; padding: 8px; }\n')
        file.write('th { background-color: #444; color: #f2f2f2; }\n')
        file.write('tr:nth-child(even) { background-color: #3e3e3e; }\n')
        file.write('tr:nth-child(odd) { background-color: #2e2e2e; }\n')
        file.write('span.copyable { cursor: pointer; color: #ffffff; }\n')
        file.write('.checked { color: white; visibility: hidden; font-size: large; }\n')
        file.write('.filters { display: flex; justify-content: space-between; align-items: center; margin-top: 20px; }\n')
        file.write('label { margin-right: 10px; }\n')
        file.write('select, input { background-color: #3e3e3e; color: #f2f2f2; border: 1px solid #444; border-radius: 5px; padding: 5px; margin: 5px; }\n')
        file.write('.contact-link { position: absolute; top: 10px; right: 10px; color: #f2f2f2; text-decoration: none; font-weight: bold; background-color: #444; padding: 5px 10px; border-radius: 5px;}')
        file.write('.contact-link:hover { background-color: #666;}')
        file.write('</style>\n')
        file.write('<script>\n')
        file.write('function applyFilters() {\n')
        file.write('    var minId = parseInt(document.getElementById("minId").value) || 0;\n')
        file.write('    var maxId = parseInt(document.getElementById("maxId").value) || Infinity;\n')
        file.write('    var filterValue = document.getElementById("filter").value;\n')
        file.write('    var rows = document.querySelectorAll("table tr:not(:first-child)");\n')
        file.write('    var nameCounts = {};\n')
        file.write('    var visibleRows = [];\n')
        file.write('    for (var i = 0; i < rows.length; i++) {\n')
        file.write('        var idCell = parseInt(rows[i].querySelectorAll("td")[0].textContent);\n')
        file.write('        var nameCell = rows[i].querySelectorAll("td")[2].textContent;\n')
        file.write('        if (idCell >= minId && idCell <= maxId) {\n')
        file.write('            nameCounts[nameCell] = (nameCounts[nameCell] || 0) + 1;\n')
        file.write('        }\n')
        file.write('    }\n')
        file.write('    for (var i = 0; i < rows.length; i++) {\n')
        file.write('        var idCell = parseInt(rows[i].querySelectorAll("td")[0].textContent);\n')
        file.write('        var countCell = rows[i].querySelectorAll("td")[3];\n')
        file.write('        var nameCell = rows[i].querySelectorAll("td")[2].textContent;\n')
        file.write('        var showById = idCell >= minId && idCell <= maxId;\n')
        file.write('        var showByCount = filterValue === "" || nameCounts[nameCell] == filterValue;\n')
        file.write('        if (showById && showByCount) {\n')
        file.write('            countCell.textContent = "(" + nameCounts[nameCell] + ")";\n')
        file.write('            visibleRows.push(rows[i]);\n')
        file.write('        } else {\n')
        file.write('            rows[i].style.display = "none";\n')
        file.write('        }\n')
        file.write('    }\n')
        file.write('    for (var i = 0; i < visibleRows.length; i++) {\n')
        file.write('        visibleRows[i].style.display = "";\n')
        file.write('        if (i % 2 === 0) {\n')
        file.write('            visibleRows[i].style.backgroundColor = "#3e3e3e";\n')
        file.write('        } else {\n')
        file.write('            visibleRows[i].style.backgroundColor = "#2e2e2e";\n')
        file.write('        }\n')
        file.write('    }\n')
        file.write('}\n')
        file.write('function copyName(name) {\n')
        file.write('    navigator.clipboard.writeText(name);\n')
        file.write('    document.querySelectorAll("span.copyable").forEach(function(elem) {\n')
        file.write('        if (elem.textContent === name) {\n')
        file.write('            elem.parentNode.querySelector(".checked").style.visibility = "visible";\n')
        file.write('        }\n')
        file.write('    });\n')
        file.write('}\n')
        file.write('</script>\n')
        file.write('</head>\n')
        file.write('<body>\n')
        file.write('<a href="https://t.me/monejey" class="contact-link">Связаться: t.me/monejey</a>')
        file.write('<div class="header">BizChecker by Monejey</div>\n')
        file.write('<div class="filters">\n')
        file.write('<div>\n')
        file.write('<label for="filter">Фильтр по количеству бизнесов:</label>\n')
        file.write('<select id="filter" onchange="applyFilters()">\n')
        file.write('<option value="">Все</option>\n')
        for count in sorted(set(name_counts.values())):
            file.write(f'<option value="{count}">{count}</option>\n')
        file.write('</select>\n')
        file.write('</div>\n')
        file.write('<div>\n')
        file.write('<label for="minId">Минимальный ID:</label>\n')
        file.write('<input type="number" id="minId" name="minId" oninput="applyFilters()">\n')
        file.write('<label for="maxId">Максимальный ID:</label>\n')
        file.write('<input type="number" id="maxId" name="maxId" oninput="applyFilters()">\n')
        file.write('</div>\n')
        file.write('</div>\n')
        file.write('<table>\n')
        file.write('<tr><th>Номер</th><th>Тип бизнеса</th><th>Ник</th><th>Повторения</th></tr>\n')
        for name, business_type, num in names_and_types:
            count = name_counts[name]
            file.write(f'<tr><td>{num}</td><td>{business_type}</td><td><span class="copyable" title="Нажмите для копирования" onclick="copyName(\'{name}\');">{name}</span><span class="checked">&#10003;</span></td><td>{count}</td></tr>\n')
        file.write('</table>\n')
        file.write('</body>\n')
        file.write('</html>\n')
    print(f"Результаты сохранены в файл {output_file}")
    return output_file

# Функция для отправки файла через бота
async def send_file(chat_id, file_path):
    try:
        with open(file_path, 'rb') as file:
            bot.send_document(chat_id, file)
    except Exception as e:
        bot.send_message(chat_id, f'Произошла ошибка при отправке файла: {e}')

# Функция-обертка для асинхронной функции
def run_main_with_param(param, label, chat_id):
    asyncio.run(main(param, label, chat_id))

if __name__ == '__main__':
    bot.polling(none_stop=True)