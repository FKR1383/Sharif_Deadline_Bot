import datetime
import main
from mysql import connector
from mysql.connector import connect, Error
import schedule
from time import sleep
from datetime import datetime, timedelta
import requests
from persiantools.jdatetime import JalaliDateTime

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
                        jalali_date = JalaliDateTime(deadline)
                        text = f'''ددلاین درس {course_name} با موضوع {event} و توضیحات {descrition} 3 روز دیگر است!
                                                زمان دقیق : {jalali_date.strftime("%H:%M:%S %Y/%m/%d")}'''
                        SEND_MESSAGE_API= 'https://api.telegram.org/bot' + main.TOKEN + '/sendMessage?chat_id=' + str(user_id) + '&text=' + text
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
                        jalali_date = JalaliDateTime(deadline)
                        text = f'''ددلاین درس {course_name} با موضوع {event} و توضیحات {descrition} 1 روز دیگر است!
                                                                        زمان دقیق : {jalali_date.strftime("%H:%M:%S %Y/%m/%d")}'''
                        SEND_MESSAGE_API = 'https://api.telegram.org/bot' + main.TOKEN + '/sendMessage?chat_id=' + str(
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
                        jalali_date = JalaliDateTime(deadline)
                        text = f'''ددلاین درس {course_name} با موضوع {event} و توضیحات {descrition} به پایان رسید!
                                                                                            زمان دقیق : {jalali_date.strftime("%H:%M:%S %Y/%m/%d")}'''
                        SEND_MESSAGE_API = 'https://api.telegram.org/bot' + main.TOKEN + '/sendMessage?chat_id=' + str(
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
