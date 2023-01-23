from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import urllib.request
import json
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
token_tg = "TOKEN"
player_tag="#RUQ0JU2P"
key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjA5ZWI1Y2VmLWM3YzgtNDkzZi04OWMwLTY5N2U3ODg4M2EzNCIsImlhdCI6MTY3NDQ4MjI1Miwic3ViIjoiZGV2ZWxvcGVyL2ZmOTFjNGY5LWJjOTgtMjgwNS1jNmIxLTdkY2RhZDg0MGI3YSIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI5NS44My4xMzIuODciXSwidHlwZSI6ImNsaWVudCJ9XX0.igL4bOo6mg7vf6HVj-RZGl8r1u4Y3sQw2nyyHIE8_4nMv79dDCxckVjWhgllTzz6q2ug--Qd4fmJT391cPg2eA"
base_url = "https://api.clashroyale.com/v1"
reply_keyboard = [
    ["Сундуки", "Винрейт", "Выход"]
]
SUCCESS, GET_TOKEN = range(2)
player_tag=""
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
def call_to_data(base_url, key, player_token):
    try:
        global player_tag
        player_tag = player_token.replace('#', '%23')    #for http request
        request = urllib.request.Request(
        base_url+f"/players/{player_tag}/upcomingchests",
        None,
        )
        request.add_header("Authorization","Bearer %s" % key)
        response = urllib.request.urlopen(request).read().decode("utf-8")
        return True
        
    except urllib.error.HTTPError: 
        return False
    


#TELEGRAM




async def is_valid(update: Update, context: ContextTypes.DEFAULT_TYPE,)-> int:
    chat_id = update.effective_chat.id
    player_token = update.message.text.upper()
    count=0
    if player_token[0] !='#':
        incorrect_token(update, context, chat_id)
    else:
        for x in player_token:
            count+=1
            if x not in "1234567890QWERTYUIOPASDFGHJKLZXCVBNM#":
                incorrect_token(update, context, chat_id)
                break
            elif count==len(player_token):
                if call_to_data(base_url, key, player_token):
                    await update.message.reply_text(text="Успешно",reply_markup=markup)
                    return SUCCESS
                else:
                    await update.message.reply_text(text="Такого токена не существует", reply_markup=ReplyKeyboardRemove())
                    return GET_TOKEN
            

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE,)-> int:
    await update.message.reply_text(text="Отправь токен игрока")
    return GET_TOKEN
async def incorrect_token(update: Update,)-> int:
    await update.message.reply_text(text="Неверный токен игрока.Попробуйте снова")

async def get_chests(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    request = urllib.request.Request(
        base_url+f"/players/{player_tag}/upcomingchests",
        None,
        )
    request.add_header("Authorization","Bearer %s" % key)
    response = urllib.request.urlopen(request).read().decode("utf-8")
    json_format = json.loads(response)
    chest_items = json_format["items"]
    sorted_chests = {}
    string_chest = ""
    for x in chest_items:
        sorted_chests[x["index"]]= x["name"]    
        string_chest = string_chest + str(x["index"]) + " : " + str(x["name"]) + "\n"
    await update.message.reply_text(text=string_chest, reply_markup=markup)

async def get_winrate(update: Update, context: ContextTypes.DEFAULT_TYPE,)-> int:
    request = urllib.request.Request(
        base_url+f"/players/{player_tag}/battlelog",
        None,
        )
    request.add_header("Authorization","Bearer %s" % key)
    response = urllib.request.urlopen(request).read().decode("utf-8")
    json_format = json.loads(response)
    wins = 0
    for x in range(len(json_format)):
        if json_format[x].get("team")[0].get("crowns") > json_format[x].get("opponent")[0].get("crowns"):
            wins+=1
    winrate=str(wins/len(json_format)*100)+"%"
    winrate_msg=f"Ваш винрейт составляет {winrate} за последние {len(json_format)} боев"
    await update.message.reply_text(text=winrate_msg, reply_markup=markup)
    

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE,)-> int:
    await update.message.reply_text("Для продолжения диалога введите /start",
        reply_markup=ReplyKeyboardRemove()),
    return ConversationHandler.END

if __name__ == "__main__":
    application = Application.builder().token(token_tg).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_TOKEN:[
                MessageHandler(filters.Regex("#"), is_valid)
            ],
            SUCCESS: [
                MessageHandler(
                    filters.Regex("^Сундуки$"),get_chests
                ),
                MessageHandler(filters.Regex("^Винрейт$"), get_winrate),
                #MessageHandler(filters.Regex("^Винрейт$"), call_to_data),      
                ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Выход$"), done)],
    )

    application.add_handler(conv_handler)
    application.run_polling()