import telebot
from parsers import parse_symptoms, parse_drugs

TOKEN = "твой токен"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "Бот не заменяет врача! Информация для ознакомления.\n\n"
        "Команды нужно вводить строго без ошибок:\n"
        "/symptoms <симптом> — например: /symptoms кашель\n"
        "/drugs <болезнь> — например: /drugs ангина\n\n"
        "Если не указать симптом или болезнь, бот попросит ввести их отдельно."
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['symptoms'])
def symptoms_cmd(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        msg = bot.reply_to(message, "Введите ваши симптомы следующим сообщением:")
        bot.register_next_step_handler(msg, symptoms_step)
        return
    bot.reply_to(message, parse_symptoms(parts[1]))

def symptoms_step(message):
    if message.text.startswith('/'):
        bot.reply_to(message, "Поиск отменён.")
        return
    bot.reply_to(message, parse_symptoms(message.text))

@bot.message_handler(commands=['drugs'])
def drugs_cmd(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        msg = bot.reply_to(message, "Введите название болезни:")
        bot.register_next_step_handler(msg, drugs_step)
        return
    bot.reply_to(message, "Ищу лекарства...")
    bot.reply_to(message, parse_drugs(parts[1]))

def drugs_step(message):
    if message.text.startswith('/'):
        bot.reply_to(message, "Поиск отменён.")
        return
    bot.reply_to(message, "Ищу лекарства...")
    bot.reply_to(message, parse_drugs(message.text))

@bot.message_handler(func=lambda m: True)
def unknown(message):
    if message.text.startswith('/'):
        bot.reply_to(message, "Неизвестная команда. Используйте /start.")
    else:
        bot.reply_to(message, "Используйте команды: /symptoms, /drugs")

print("Бот запущен...")
bot.infinity_polling(timeout=60, long_polling_timeout=30)
