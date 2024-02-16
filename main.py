import responses, queries
from typing import Final
from telegram import Update
import deadline_notification
from threading import Thread
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mysql.connector import connect, Error
import schedule
from time import sleep
from datetime import datetime, timedelta
import requests
from threading import Thread
from persiantools.jdatetime import JalaliDateTime

TOKEN: Final = '6898166331:AAGTDTbN7Srdv9094YJlpnKVshhXp7iJcLg'
BOT_USERNAME: Final = '@Sharif_Deadline_bot'

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(responses.START_FIRST_TEXT)
    await update.message.reply_text(responses.START_SECOND_TEXT)
    await queries.add_user_to_database(update)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(responses.HELP_TEXT)

async def my_deadlines_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with connect(
            host="localhost",
            user="admin",
            password="admin00",
            database="sharif_deadline_database"
        ) as connection:
            with connection.cursor() as cursor:
                user_id = update.message.chat.id
                sql_select_Query = queries.all_my_courses_query(user_id)
                cursor = connection.cursor()
                cursor.execute(sql_select_Query)
                records = cursor.fetchall()
                result = ''
                course_names = []
                course_ids = []
                for row in records:
                    course_ids.append(row[0])
                    course_names.append(row[1])
                for i in range(len(course_ids)):
                    course_name = course_names[i]
                    course_id = course_ids[i]
                    result = result + course_name + ":\n"
                    sql_select_Query = queries.deadlines_with_details_query(course_id)
                    cursor = connection.cursor()
                    cursor.execute(sql_select_Query)
                    records = cursor.fetchall()
                    for row in records:
                        jalali_date = JalaliDateTime(row[2])
                        result = result + row[0] + " | " + row[1] + " | " + jalali_date.strftime("%H:%M:%S %Y/%m/%d") + "\n"
                await update.message.reply_text(result)
    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

async def all_courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = await queries.get_all_courses_from_database()
    await update.message.reply_text(result)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    print(responses.user_message_text(update.message.chat.username, message_type, text))
    if message_type == 'private':
        parts = text.split('-')
        course_id = int(parts[0])
        group_id = int(parts[1])
        response = await queries.add_or_remove_course(course_id, group_id, int(update.message.chat.id))
        print(responses.bot_message_response(response, update.message.chat.username))
        await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

async def my_courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with connect(
                host="localhost",
                user="admin",
                password="admin00",
                database="sharif_deadline_database"
        ) as connection:
            with connection.cursor() as cursor:
                user_id = update.message.chat.id
                sql_select_Query = queries.my_courses_with_details_query(user_id)
                cursor = connection.cursor()
                cursor.execute(sql_select_Query)
                records = cursor.fetchall()
                result = ''
                for row in records:
                    result += ("کد درس = " + str(row[0])) + ' | '
                    result += ("کد گروه = " + str(row[1])) + ' | '
                    result += ("اسم درس = " + str(row[2])) + ' | '
                    result += ("اسم اساتید = " + str(row[3])) + ' | '
                    result += '\n'
                await update.message.reply_text(result)
    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("MySQL connection is closed")


if __name__ == "__main__":
    queries.connect_to_database()
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    #Handle deadline notificatios using Thread
    thread = Thread(target=deadline_notification.deadline_notification)
    thread.start()

    #Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('courses', all_courses_command))
    app.add_handler(CommandHandler('my_courses', my_courses_command))
    app.add_handler(CommandHandler('my_deadlines', my_deadlines_command))

    #Messages - now only for adding new course to my_courses or remove course from it
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Errors
    app.add_error_handler(error)

    #Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)
