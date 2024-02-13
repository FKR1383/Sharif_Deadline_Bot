import threading
from typing import Final
from telegram import Update
from threading import Thread
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mysql.connector import connect, Error
import schedule
from time import sleep
from datetime import datetime, timedelta
import requests
from threading import Thread
from persiantools.jdatetime import JalaliDate


BOT_USERNAME: Final = '@Sharif_Deadline_bot'

async def add_user_to_database(update: Update):
    try:
        connection = connect(host='localhost',
                                             database='sharif_deadline_database',
                                             user='admin',
                                             password='admin00')

        sql_select_Query = f"SELECT * FROM users WHERE users.user_id = {update.message.chat.id} and users.username= '{update.message.chat.username}'"
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        if cursor.rowcount == 0:
            mySql_insert_query = f"""INSERT INTO users (user_id, username) 
                               VALUES 
                                   ({update.message.chat.id}, '{update.message.chat.username}') """
            cursor = connection.cursor()
            cursor.execute(mySql_insert_query)
            connection.commit()
            print(cursor.rowcount, "User added!")
            cursor.close()
        else:
            print('old user!')
            cursor.close()

    except Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed")



# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام. به ربات اعلام ددلاین شریف خوش آمدید :) در اسرع وقت اسم درس هاتو بگو که بتونم کمکت کنم. (لیست دروس رو برات گذاشتیم :) )")
    await update.message.reply_text("حتما یه سر به بخش help بات بزن تا بفهمی چجوری باهاش کار کنی")
    await add_user_to_database(update)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("برای افزودن درس در صورتی که درس رو در لیست دروست نداری، کافیه کد درس رو به همراه کد گروهش به فرمت زیر وارد کنی تا درس رو برات اضافه کنم\n40181-1\nاگه هم درسی رو توی لیست دروس من داری و میخوای حذفش کنی کافیه مشابه بالا کد درس رو با شماره گروهش بگی تا حذف بشه")



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

async def add_or_remove_course(course_id, group_id, user_id):
    try:
        connection = connect(host='localhost',
                                             database='sharif_deadline_database',
                                             user='admin',
                                             password='admin00')
        sql_select_Query = f"""SELECT * FROM course
         INNER JOIN user_course_relation on  user_course_relation.course_table_id = course.id
         INNER JOIN users on users.id = user_course_relation.user_table_id
    WHERE users.user_id = {user_id} and course.course_id = {course_id} and course.group_id = {group_id}
    """
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        if cursor.rowcount != 0:
            # Delete a record
            sql_select_Query = f"""SELECT * FROM user_course_relation
                  INNER JOIN course on  user_course_relation.course_table_id = course.id
                  INNER JOIN users on users.id = user_course_relation.user_table_id
WHERE users.user_id = {user_id} and course.course_id = {course_id} and course.group_id = {group_id}
                """
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            id_of_record = records[0][0]
            sql_select_Query = f"""SELECT * FROM course
                     INNER JOIN user_course_relation on  user_course_relation.course_table_id = course.id
                     INNER JOIN users on users.id = user_course_relation.user_table_id
                WHERE users.user_id = {user_id} and course.course_id = {course_id} and course.group_id = {group_id}
                """
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            course_name = records[0][2]
            sql_Delete_query = f"""Delete from user_course_relation 
    WHERE user_course_relation.id = {id_of_record}"""
            cursor.execute(sql_Delete_query)
            connection.commit()
            return f'درس {course_name} از لیست دروس من حذف شد.'
        else:
            sql_select_Query = f"""SELECT * FROM course
                WHERE course.course_id = {course_id} and course.group_id = {group_id}
                """
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            if cursor.rowcount == 0:
                return 'چنین درسی وجود ندارد!'
            course_table_id = records[0][0]
            course_name = records[0][2]
            sql_select_Query = f"""SELECT * FROM users
                            WHERE users.user_id = {user_id}
                            """
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            user_table_id = records[0][0]
            mySql_insert_query = f"""INSERT INTO user_course_relation(user_table_id, course_table_id)
            VALUES({user_table_id} ,{course_table_id})
    """
            cursor = connection.cursor()
            cursor.execute(mySql_insert_query)
            connection.commit()
            return f'درس {course_name} با موفقیت افزوده شد.'

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'private':
        parts = text.split('-')
        course_id = int(parts[0])
        group_id = int(parts[1])
        response = await add_or_remove_course(course_id, group_id, int(update.message.chat.id))
        print('Bot:', response)
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
                sql_select_Query = f"""SELECT course_id, group_id, course_name, lecturers_name FROM course
                                         INNER JOIN user_course_relation on  user_course_relation.course_table_id = course.id
                                         INNER JOIN users on users.id = user_course_relation.user_table_id
                                    WHERE users.user_id = {user_id}
                                    """
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

def deadline_notification():
    while True:
        now = datetime.now()
        current_time = now.strftime("%m/%d/%Y %H:%M")
        try:
            connection = connect(host='localhost',
                                 database='sharif_deadline_database',
                                 user='admin',
                                 password='admin00')
            sql_select_Query = f"SELECT * FROM deadline"
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            deadline_ids = []
            deadline_times = []
            events = []
            descriptions = []
            ended_deadline_ids = []
            for row in records:
                deadline_ids.append(row[0])
                deadline_times.append(row[4])
                events.append(row[2])
                descriptions.append(row[3])
            for i in range(len(deadline_ids)):
                deadline = deadline_times[i]
                deadline_id = deadline_ids[i]
                event = events[i]
                descrition = descriptions[i]
                three_days_before = deadline - timedelta(days=3)
                one_day_before = deadline - timedelta(days=1)
                if current_time == three_days_before.strftime("%m/%d/%Y %H:%M"):
                    sql_select_Query = f"SELECT course_group_id FROM deadline WHERE id = {deadline_id}"
                    cursor = connection.cursor()
                    cursor.execute(sql_select_Query)
                    records = cursor.fetchall()
                    course_id = records[0][0]
                    sql_select_Query = f"SELECT course_name FROM course WHERE id = {course_id}"
                    cursor = connection.cursor()
                    cursor.execute(sql_select_Query)
                    records = cursor.fetchall()
                    course_name = records[0][0]
                    sql_select_Query = f"""SELECT user_id from users
INNER JOIN user_course_relation ON user_course_relation.user_table_id = users.id
INNER JOIN deadline ON deadline.course_group_id = user_course_relation.course_table_id
INNER JOIN course ON course.id = user_course_relation.course_table_id
WHERE deadline.id = {deadline_id}"""
                    cursor = connection.cursor()
                    cursor.execute(sql_select_Query)
                    records = cursor.fetchall()
                    for row in records:
                        user_id = row[0]
                        jalali_date = JalaliDate(deadline)
                        text = f'''ددلاین درس {course_name} با موضوع {event} و توضیحات {descrition} 3 روز دیگر است!
                                                زمان دقیق : {jalali_date.strftime("%H:%M:%S %Y:%m:%d")}'''
                        SEND_MESSAGE_API= 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + str(user_id) + '&text=' + text
                        requests.get(SEND_MESSAGE_API)
                elif current_time == one_day_before.strftime("%m/%d/%Y %H:%M"):
                    #print('one day before')
                    sql_select_Query = f"SELECT course_group_id FROM deadline WHERE id = {deadline_id}"
                    cursor = connection.cursor()
                    cursor.execute(sql_select_Query)
                    records = cursor.fetchall()
                    course_id = records[0][0]
                    sql_select_Query = f"SELECT course_name FROM course WHERE id = {course_id}"
                    cursor = connection.cursor()
                    cursor.execute(sql_select_Query)
                    records = cursor.fetchall()
                    course_name = records[0][0]
                    sql_select_Query = f"""SELECT user_id from users
                    INNER JOIN user_course_relation ON user_course_relation.user_table_id = users.id
                    INNER JOIN deadline ON deadline.course_group_id = user_course_relation.course_table_id
                    INNER JOIN course ON course.id = user_course_relation.course_table_id
                    WHERE deadline.id = {deadline_id}"""
                    cursor = connection.cursor()
                    cursor.execute(sql_select_Query)
                    records = cursor.fetchall()
                    for row in records:
                        print("I'm here")
                        user_id = row[0]
                        jalali_date = JalaliDate(deadline)
                        text = f'''ددلاین درس {course_name} با موضوع {event} و توضیحات {descrition} 1 روز دیگر است!
                                                                        زمان دقیق : {jalali_date.strftime("%H:%M:%S %Y:%m:%d")}'''
                        SEND_MESSAGE_API = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + str(
                            user_id) + '&text=' + text
                        requests.get(SEND_MESSAGE_API)
                elif current_time == ((deadline + timedelta(minutes=1)).strftime("%m/%d/%Y %H:%M")):
                    ended_deadline_ids.append(deadline_id)
                    sql_select_Query = f"SELECT course_group_id FROM deadline WHERE id = {deadline_id}"
                    cursor = connection.cursor()
                    cursor.execute(sql_select_Query)
                    records = cursor.fetchall()
                    course_id = records[0][0]
                    sql_select_Query = f"SELECT course_name FROM course WHERE id = {course_id}"
                    cursor = connection.cursor()
                    cursor.execute(sql_select_Query)
                    records = cursor.fetchall()
                    course_name = records[0][0]
                    sql_select_Query = f"""SELECT user_id from users
                                        INNER JOIN user_course_relation ON user_course_relation.user_table_id = users.id
                                        INNER JOIN deadline ON deadline.course_group_id = user_course_relation.course_table_id
                                        INNER JOIN course ON course.id = user_course_relation.course_table_id
                                        WHERE deadline.id = {deadline_id}"""
                    cursor = connection.cursor()
                    cursor.execute(sql_select_Query)
                    records = cursor.fetchall()
                    for row in records:
                        print("I'm here")
                        user_id = row[0]
                        jalali_date = JalaliDate(deadline)
                        text = f'''ددلاین درس {course_name} با موضوع {event} و توضیحات {descrition} به پایان رسید!
                                                                                            زمان دقیق : {jalali_date.strftime("%H:%M:%S %Y:%m:%d")}'''
                        SEND_MESSAGE_API = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + str(
                            user_id) + '&text=' + text
                        requests.get(SEND_MESSAGE_API)
            for i in range(len(ended_deadline_ids)):
                sql_Delete_query = f"""Delete from deadline 
                    WHERE id = {ended_deadline_ids[i]}"""
                cursor.execute(sql_Delete_query)
                connection.commit()
        except Error as error:
            print("Failed to insert record into Laptop table {}".format(error))
        finally:
            if connection.is_connected():
                connection.close()
                print("MySQL connection is closed")
        schedule.run_pending()
        sleep(59)

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
                sql_select_Query = f"""SELECT course.id, course_name FROM course
                                INNER JOIN user_course_relation on  user_course_relation.course_table_id = course.id
                                INNER JOIN users on users.id = user_course_relation.user_table_id
WHERE users.user_id = {user_id}
                                """
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
                    sql_select_Query = f"""SELECT event, desctiption, time FROM deadline WHERE course_group_id = {course_id} ORDER BY time ASC
                                                    """
                    cursor = connection.cursor()
                    cursor.execute(sql_select_Query)
                    records = cursor.fetchall()
                    for row in records:
                        jalali_date = JalaliDate(row[2])
                        result = result + row[0] + " | " + row[1] + " | " + jalali_date.strftime("%H:%M:%S %Y:%m:%d") + "\n"
                await update.message.reply_text(result)
    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    connect_to_database()
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()
    thread = Thread(target=deadline_notification)
    thread.start()
    #Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('courses', all_courses_command))
    app.add_handler(CommandHandler('my_courses', my_courses_command))
    app.add_handler(CommandHandler('my_deadlines', my_deadlines_command))


    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Errors
    app.add_error_handler(error)

    #Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)



