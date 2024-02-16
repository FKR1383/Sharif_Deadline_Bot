from telegram import Update
from mysql.connector import connect, Error

def my_courses_with_details_query(user_id):
    return f"""SELECT course_id, group_id, course_name, lecturers_name FROM course
                                         INNER JOIN user_course_relation on  user_course_relation.course_table_id = course.id
                                         INNER JOIN users on users.id = user_course_relation.user_table_id
                                    WHERE users.user_id = {user_id}
                                    """

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

def all_my_courses_query(user_id):
    return f"""SELECT course.id, course_name FROM course
                                INNER JOIN user_course_relation on  user_course_relation.course_table_id = course.id
                                INNER JOIN users on users.id = user_course_relation.user_table_id
WHERE users.user_id = {user_id}
                                """

def deadlines_with_details_query(course_id):
    return f"""SELECT event, desctiption, time FROM deadline WHERE course_group_id = {course_id} ORDER BY time ASC
                                                        """

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