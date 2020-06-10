"""A telegram bot for Apollo HR XE.

This module uses apollo.py to communicate with Apollo HR XE and
uses apollodb.py for user management.
"""
import logging
import sys
import os
import datetime
import random
from functools import partial
from telegram.ext import Updater, CommandHandler, CallbackContext
import apollodb
import apollo


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logging.info("Starting...")


logging.info("Import finished, setting up functions...")

bot_token = os.environ.get("BOT_TOKEN", None)
if not bot_token:
    logging.error("No bot token, exiting...")
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    """Command handler: /start - displays help."""
    logging.info(f"Command: /start triggered by {update.effective_chat.id}")
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="""I can perform the following actions:
        /start - show this message
        /login <username> <password> - save your info to a database
        /info - retrieve your current information
        /clock <in/out> - clock in or out
        /reminder <on/off> - turn on/off reminder
        /autolog <on/off> - turn on/off auto clock in
        /delete - delete everything about you from my database.""",
    )


def login(update, context):
    """Command handler: /login <username> <password> - save login to database."""
    logging.info(f"Command: /login triggered by {update.effective_chat.id}")
    if len(context.args) != 2:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Not enough or too many parameters, I need both usernamae and password.",
        )
    else:
        ses = apollodb.UserQuery(apollodb.Session())
        u = ses.get_user(update.effective_chat.id)
        if u:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Your user already exists, I'm going to delete it and create a new one.",
            )
            ses.delete(update.effective_chat.id)
        new_user = apollodb.User(
            userid=update.effective_chat.id,
            apollo_user=context.args[0],
            apollo_password=context.args[1],
        )
        ses.add_user(new_user)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Your login information is now saved.",
        )
        ses.close()


def info(update, context):
    """Command handler: /info - check database info."""
    logging.info(f"Command: /info triggered by {update.effective_chat.id}")
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
    """Command handler: /clock <in/out> - clock in or out."""
    logging.info(f"Command: /clock triggered by {update.effective_chat.id}")
    if len(context.args) != 1:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Not enough or too many parameters, clock either in or out.",
        )
    else:
        ses = apollodb.UserQuery(apollodb.Session())
        u = ses.get_user(update.effective_chat.id)
        if u:
            if context.args[0] == "in":
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Attempting to clock you in...",
                )
                br = apollo.ApolloSession()
                login_status = br.login(u.apollo_user, u.apollo_password)
                if str(login_status) == "True":
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Login successful, starting clock-in...",
                    )
                    msg = br.clock_in()
                    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Login unsuccessful, check your username or password...",
                    )
                del br
            elif context.args[0] == "out":
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Attempting to clock you out...",
                )
                br = apollo.ApolloSession()
                login_status = br.login(u.apollo_user, u.apollo_password)
                if str(login_status) == "True":
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Login successful, starting clock-out...",
                    )
                    msg = br.clock_out()
                    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Login unsuccessful, check your username or password...",
                    )
                del br
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text="Clock either in or out..."
                )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="I don't have any information on you. /login first.",
            )
        ses.close()


def reminder(update, context):
    """Command handler: /reminder <on/off> - set clock reminder on or off."""
    logging.info(f"Command: /reminder triggered by {update.effective_chat.id}")
    if len(context.args) != 1:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Not enough or too many parameters, reminder either on or off.",
        )
    else:
        ses = apollodb.UserQuery(apollodb.Session())
        u = ses.get_user(update.effective_chat.id)
        if u:
            if context.args[0] == "on":
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="I will remind you to clock in and out.",
                )
                ses.set_reminder(update.effective_chat.id, True)
            elif context.args[0] == "off":
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="I will stop reminding you to clock in and out. Autolog is also disabled.",
                )
                ses.set_reminder(update.effective_chat.id, False)
                ses.set_autolog(update.effective_chat.id, False)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text="Sorry, I don't understand."
                )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="I don't have any information on you. /login first.",
            )
        ses.close()


def autolog(update, context):
    """Command handler: /autolog <on/off> - set autolog on or off."""
    logging.info(f"Command: /autolog triggered by {update.effective_chat.id}")
    if len(context.args) != 1:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Not enough or too many parameters, autolog either on or off.",
        )
    else:
        ses = apollodb.UserQuery(apollodb.Session())
        u = ses.get_user(update.effective_chat.id)
        if u:
            if context.args[0] == "on":
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="I will automatically clock you in and out. Reminder is also enabled.",
                )
                ses.set_reminder(update.effective_chat.id, True)
                ses.set_autolog(update.effective_chat.id, True)
            elif context.args[0] == "off":
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="I will stop automatically clocking you in and out.",
                )
                ses.set_autolog(update.effective_chat.id, False)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text="Sorry, I don't understand."
                )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="I don't have any information on you. /login first.",
            )
        ses.close()


def delete(update, context):
    """Command handler: /delete - delete all info."""
    logging.info(f"Command: /delete triggered by {update.effective_chat.id}")
    ses = apollodb.UserQuery(apollodb.Session())
    u = ses.get_user(update.effective_chat.id)
    if u:
        ses.delete(update.effective_chat.id)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Your user information has been deleted.",
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="I couldn't find your information."
        )
    ses.close()


start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)
login_handler = CommandHandler("login", login)
dispatcher.add_handler(login_handler)
info_handler = CommandHandler("info", info)
dispatcher.add_handler(info_handler)
clock_handler = CommandHandler("clock", clock)
dispatcher.add_handler(clock_handler)
reminder_handler = CommandHandler("reminder", reminder)
dispatcher.add_handler(reminder_handler)
autolog_handler = CommandHandler("autolog", autolog)
dispatcher.add_handler(autolog_handler)
delete_handler = CommandHandler("delete", delete)
dispatcher.add_handler(delete_handler)

j = updater.job_queue


def callback_clock(context: CallbackContext, out: bool = False):
    """Handle callback: a clock in/out callback using job queue."""
    u = context.job.context
    clock_string = "clockin_"
    if out:
        clock_string = "clockout_"
    logging.info(f"{clock_string}: {str(u.userid)}")
    br = apollo.ApolloSession()
    retry_count = 3
    for i in range(retry_count):
        login_status = br.login(u.apollo_user, u.apollo_password)
        if str(login_status) == "True":
            msg = br.work_day_query()
            if msg == "work":
                logging.info(f"{clock_string}{str(u.userid)}: Detected Work Day")
                work_detected_text = "Good morning, you have work today!"
                if out:
                    work_detected_text = "Good evening, nice work today!"
                context.bot.send_message(
                    chat_id=u.userid, text=work_detected_text,
                )
                if u.autolog:
                    logging.info(f"{clock_string}{str(u.userid)}: Auto Login")
                    context.bot.send_message(
                        chat_id=u.userid,
                        text=f"You have autolog enabled, I will now try to clock you {'out' if out else 'in'}.",
                    )
                    if out:
                        clock_msg = br.clock_out()
                    else:
                        clock_msg = br.clock_in()
                    logging.info(f"{clock_string}{str(u.userid)} Login:" + clock_msg)
                    context.bot.send_message(chat_id=u.userid, text=clock_msg)
            elif msg == "leave":
                logging.info(f"{clock_string}{str(u.userid)}: Detected Leave Day")
                context.bot.send_message(
                    chat_id=u.userid,
                    text=f"Good evening, I detected a leave notice today, but I'm still sending you a reminder to clock {'out' if out else 'in'}!",
                )
                if u.autolog:
                    context.bot.send_message(
                        chat_id=u.userid,
                        text=f"Since I can't tell your leave hours, you'll have to clock {'out' if out else 'in'} manually!",
                    )
            elif msg == "off":
                logging.info(f"{clock_string}{str(u.userid)}: Detected Off Day")
                pass
            else:
                logging.info(f"{clock_string}{str(u.userid)}: Detected " + msg)
                pass
            break
        else:
            logging.info(f"{clock_string}{str(u.userid)}: " + login_status)
            if i == retry_count - 1:
                context.bot.send_message(
                    chat_id=u.userid,
                    text=f"Login failed {retry_count} times.\n"
                    + login_status
                    + "\nPlease clock in/out manually.",
                )
    del br


def callback_reminder_clock(context: CallbackContext, out: bool = False):
    """Handle callback: a clock in/out reminder schedule using job queue."""
    ses = apollodb.UserQuery(apollodb.Session())
    us = ses.get_reminder()
    clock_string = "clockin_"
    if out:
        clock_string = "clockout_"
    for u in us:
        max_half_hour_delay = random.randint(0, 60 * 29)
        logging.info(
            f"{clock_string}: Adding a {str(max_half_hour_delay)} second delay for {str(u.userid)}"
        )
        callback_clock_function = partial(callback_clock, out=False)
        if out:
            callback_clock_function = partial(callback_clock, out=True)
        context.job_queue.run_once(
            callback_clock_function,
            max_half_hour_delay,
            context=u,
            name=clock_string + str(u.userid),
        )


job_reminder_clockin = j.run_daily(
    partial(callback_reminder_clock, out=False),
    datetime.time(23, 29),
    name="callback_reminder_clockin",
)  # 7:29 TAIWAN

job_reminder_clockout = j.run_daily(
    partial(callback_reminder_clock, out=True),
    datetime.time(9, 1),
    name="callback_reminder_clockout",
)  # 17:01 TAIWAN

logging.info("Started polling...")
updater.start_polling()
updater.idle()
