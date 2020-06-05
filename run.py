import logging
import sys
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO, stream=sys.stdout)
logging.info("Starting...")
import datetime
from telegram.ext import Updater, CommandHandler, CallbackContext
import apollodb
import apollo

logging.info("Import finished, setting up functions...")

updater = Updater(token='1***REMOVED***', use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I can perform the following actions:\n/start - show this message\n/login <username> <password> - save your info to a database\n/info - retrieve your current information\n/clock <in/out> - clock in or out\n/reminder <on/off> - turn on/off reminder\n/autolog <on/off> - turn on/off auto clock in\n/delete - delete everything about you from my database.")
def login(update, context):
    if len(context.args) != 2:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Not enough or too many parameters, I need both usernamae and password.")
    else:
        ses = apollodb.UserQuery(apollodb.Session())
        u = ses.get_user(update.effective_chat.id)
        if u:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Your user already exists, I'm going to delete it and create a new one.")
            ses.delete(update.effective_chat.id)
        new_user = apollodb.User(userid=update.effective_chat.id, apollo_user=context.args[0], apollo_password=context.args[1])
        ses.add_user(new_user)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your login information is now saved.")
        ses.close()
def info(update, context):
    ses = apollodb.UserQuery(apollodb.Session())
    u = ses.get_user(update.effective_chat.id)
    if u:
        text = "I currently have the following information:"
        text += "\nYour username: " + u.apollo_user
        text += "\nYour password: " + u.apollo_password
        text += "\nReminders are: " + ("on" if u.reminder else "off")
        text += "\nAutolog is: " + ("on" if u.autolog else "off")
    else:
        text = "I don't have any information on you."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    ses.close()
def clock(update, context):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Not enough or too many parameters, clock either in or out.")
    else:
        ses = apollodb.UserQuery(apollodb.Session())
        u = ses.get_user(update.effective_chat.id)
        if u:
            if context.args[0] == "in":
                context.bot.send_message(chat_id=update.effective_chat.id, text="Attempting to clock you in...")
                br = apollo.ApolloSession()
                login_status = br.login(u.apollo_user, u.apollo_password)
                if str(login_status) == "True":
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Login successful, starting clock-in...")
                    msg = br.clock_in()
                    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Login unsuccessful, check your username or password...")
                del br
            elif context.args[0] == "out":
                context.bot.send_message(chat_id=update.effective_chat.id, text="Attempting to clock you out...")
                br = apollo.ApolloSession()
                login_status = br.login(u.apollo_user, u.apollo_password)
                if str(login_status) == "True":
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Login successful, starting clock-out...")
                    msg = br.clock_out()
                    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Login unsuccessful, check your username or password...")
                del br
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Clock either in or out...")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="I don't have any information on you. /login first.")
        ses.close()
def reminder(update, context):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Not enough or too many parameters, reminder either on or off.")
    else:
        ses = apollodb.UserQuery(apollodb.Session())
        u = ses.get_user(update.effective_chat.id)
        if u:
            if context.args[0] == "on":
                context.bot.send_message(chat_id=update.effective_chat.id, text="I will remind you to clock in and out.")
                ses.set_reminder(update.effective_chat.id, True)
            elif context.args[0] == "off":
                context.bot.send_message(chat_id=update.effective_chat.id, text="I will stop reminding you to clock in and out. Autolog is also disabled.")
                ses.set_reminder(update.effective_chat.id, False)
                ses.set_autolog(update.effective_chat.id, False)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I don't understand.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="I don't have any information on you. /login first.")
        ses.close()
def autolog(update, context):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Not enough or too many parameters, autolog either on or off.")
    else:
        ses = apollodb.UserQuery(apollodb.Session())
        u = ses.get_user(update.effective_chat.id)
        if u:
            if context.args[0] == "on":
                context.bot.send_message(chat_id=update.effective_chat.id, text="I will automatically clock you in and out. Reminder is also enabled.")
                ses.set_reminder(update.effective_chat.id, True)
                ses.set_autolog(update.effective_chat.id, True)
            elif context.args[0] == "off":
                context.bot.send_message(chat_id=update.effective_chat.id, text="I will stop automatically clocking you in and out.")
                ses.set_autolog(update.effective_chat.id, False)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I don't understand.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="I don't have any information on you. /login first.")
        ses.close()
def delete(update, context):
    ses = apollodb.UserQuery(apollodb.Session())
    u = ses.get_user(update.effective_chat.id)
    if u:
        ses.delete(update.effective_chat.id)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your user information has been deleted.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="I couldn't find your information.")
    ses.close()

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
login_handler = CommandHandler('login', login)
dispatcher.add_handler(login_handler)
info_handler = CommandHandler('info', info)
dispatcher.add_handler(info_handler)
clock_handler = CommandHandler('clock', clock)
dispatcher.add_handler(clock_handler)
reminder_handler = CommandHandler('reminder', reminder)
dispatcher.add_handler(reminder_handler)
autolog_handler = CommandHandler('autolog', autolog)
dispatcher.add_handler(autolog_handler)
delete_handler = CommandHandler('delete', delete)
dispatcher.add_handler(delete_handler)

j = updater.job_queue

def callback_clockin(context: CallbackContext):
    u = context.job.context
    br = apollo.ApolloSession()
    login_status = br.login(u.apollo_user, u.apollo_password)
    if str(login_status) == "True":
        msg = br.work_day_query()
        if msg == "work":
            context.bot.send_message(chat_id=u.userid, text="Good morning, you have work today!")
            if u.autolog:
                context.bot.send_message(chat_id=u.userid, text="You have autolog enabled, I will now try to clock you in.")
                msg = br.clock_in()
                context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        elif msg == "leave":
            context.bot.send_message(chat_id=u.userid, text="Good morning, I detected a leave notice today!")
            if u.autolog:
                context.bot.send_message(chat_id=u.userid, text="Since I can't tell your leave hours, you'll have to clock in manually!")
        elif msg == "off":
            pass
        else:
            pass
    del br
    
def callback_clockout(context: CallbackContext):
    u = context.job.context
    br = apollo.ApolloSession()
    login_status = br.login(u.apollo_user, u.apollo_password)
    if str(login_status) == "True":
        msg = br.work_day_query()
        if msg == "work":
            context.bot.send_message(chat_id=u.userid, text="Good evening, nice work today, remember to clock out!")
            if u.autolog:
                context.bot.send_message(chat_id=u.userid, text="You have autolog enabled, I will now try to clock you out.")
                msg = br.clock_out()
                context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        elif msg == "leave":
            context.bot.send_message(chat_id=u.userid, text="Good evening, I detected a leave notice today, but I'm still sending you a reminder to clock out!")
            if u.autolog:
                context.bot.send_message(chat_id=u.userid, text="Since I can't tell your leave hours, you'll have to clock out manually!")
        elif msg == "off":
            pass
        else:
            pass
    del br

def callback_reminder_clockin(context: CallbackContext):
    ses = apollodb.UserQuery(apollodb.Session())
    us = ses.get_reminder()
    for u in us:
        context.job_queue.run_once(callback_clockin, 5, context=u)

def callback_reminder_clockout(context: CallbackContext):
    ses = apollodb.UserQuery(apollodb.Session())
    us = ses.get_reminder()
    for u in us:
        context.job_queue.run_once(callback_clockout, 5, context=u)

job_reminder_clockin = j.run_daily(callback_reminder_clockin, datetime.time(23,15)) # 7:15 TAIWAN
job_reminder_clockout = j.run_daily(callback_reminder_clockout, datetime.time(9,0)) # 17:00 TAIWAN

logging.info("Started polling...")
updater.start_polling()
updater.idle()
