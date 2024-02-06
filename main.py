from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = '6898166331:AAE3SxcJjYu01NCsbvlZHs9Gzkcj7RQmM80'
BOT_USERNAME: Final = '@Sharif_Deadline_bot'

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام. به ربات اعلام ددلاین شریف خوش آمدید :) در اسرع وقت درس هاتو بگو که بتونم کمکت کنم.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("این بات برای کمک به فراموش نکردن ددلاین ها ساخته شده.")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Nothing!")

# Handle Responses

def handle_response(text: str) -> str:
    text = text.lower()
    if 'hello' in text:
        return 'Hey Bitch!'
    if 'bye' in text:
        return 'Bye Bitch'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str =  update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '')
            response: str = handle_response(new_text)
        else:
            response: str = handle_response(text)
        print('Bot:', response)
        await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass