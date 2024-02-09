from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mysql.connector import connect, Error


BOT_USERNAME: Final = '@Sharif_Deadline_bot'

async def add_user_to_database(update: Update):
    try:
        connection = connect(host='localhost',
                                             database='sharif_deadline_database',
                                             user='admin',
                                             password='admin00')
        mySql_insert_query = f"""INSERT INTO users (user_id, username) 
                               VALUES 
                               ({update.message.chat.id}, '{update.message.chat.username}') """
        cursor = connection.cursor()
        cursor.execute(mySql_insert_query)
        connection.commit()
        print(cursor.rowcount, "User added!")
        cursor.close()

    except Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed")



# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام. به ربات اعلام ددلاین شریف خوش آمدید :) در اسرع وقت درس هاتو بگو که بتونم کمکت کنم. (لیست دروس رو برات گذاشتیم :) )")
    await add_user_to_database(update)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("این بات برای کمک به فراموش نکردن ددلاین ها ساخته شده.")

async def get_all_courses_from_database():
    try:
        connection = connect(host='localhost',
                                             database='sharif_deadline_database',
                                             user='admin',
                                             password='admin00')

        sql_select_Query = "SELECT course_id, group_id, course_name, lecturers_name FROM course"
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
        return result

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

async def all_courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = await get_all_courses_from_database()
    await update.message.reply_text(result)

# Handle Responses

def handle_response(text: str) -> str:
    text = text.lower()
    if 'hello' in text:
        return 'Hey'
    if 'bye' in text:
        return 'Bye'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'private':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '')
            response: str = handle_response(new_text)
        else:
            response: str = handle_response(text)
        print('Bot:'


              , response)
        await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

def connect_to_database():
    try:
        with connect(
                host="localhost",
                user="admin",
                password="admin00",
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Sharif_Deadline_Database.users")
                for db in cursor:
                    print(db)
    except Error as e:
        print(e)



if __name__ == "__main__":
    connect_to_database()
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    #Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('courses', all_courses_command))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Errors
    app.add_error_handler(error)

    #Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)



