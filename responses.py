START_FIRST_TEXT = "سلام. به ربات اعلام ددلاین شریف خوش آمدید :) در اسرع وقت اسم درس هاتو بگو که بتونم کمکت کنم. (لیست دروس رو برات گذاشتیم :) )"
START_SECOND_TEXT = "حتما یه سر به بخش help بات بزن تا بفهمی چجوری باهاش کار کنی"
HELP_TEXT = "برای افزودن درس در صورتی که درس رو در لیست دروست نداری، کافیه کد درس رو به همراه کد گروهش به فرمت زیر وارد کنی تا درس رو برات اضافه کنم\n40181-1\nاگه هم درسی رو توی لیست دروس من داری و میخوای حذفش کنی کافیه مشابه بالا کد درس رو با شماره گروهش بگی تا حذف بشه"

def user_message_text(username, message_type, text):
    return f'User ({username}) in {message_type}: "{text}"'

def bot_message_response(response, username):
    return f'Bot to {username}: {response}'