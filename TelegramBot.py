#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import json
import requests
import praw

Reddit = praw.Reddit('ImgToTelegram')

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

with open("TelegramConfig.json") as TelegramConfigFile:
    Configs = json.load(TelegramConfigFile)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    if (update.message.text == "Sono swag"):
        update.message.reply_text("Si lo sei")
    else:
        update.message.reply_text(update.message.text)

#if the bot recognize that you are asking the ip he'll give you the IP
def ip(update, context):
    print("/ip {} - {}".format(update.message.from_user.username, update.message.from_user.id))
    if Configs["Username"] == update.message.from_user.username and Configs["UserID"] == update.message.from_user.id:
        print("/ip {} - {}".format(update.message.from_user.username, update.message.from_user.id))
        update.message.reply_text(requests.get('https://httpbin.org/ip').json()['origin'])

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

#function to post on the telegram the things liked on Reddit
def RedditSender(context):
    for post in Reddit.redditor(Configs["RedditUsername"]).upvoted(limit=100):
        if (IsImage(post.url) and NotPosted(post.url)):
            if(CheckSubreddit(post)):
                context.bot.sendPhoto(chat_id=Configs["WallpaperChannelId"],  photo=post.url, caption=post.subreddit_name_prefixed)
                context.bot.sendDocument(chat_id=Configs["WallpaperChannelId"],  document=post.url)
            else:
                context.bot.sendPhoto(chat_id=Configs["MemeChannelId"],  photo=post.url, caption=post.subreddit_name_prefixed + ": "+ post.title + "\n" + "reddit.com" + post.permalink)
    
def CheckSubreddit(post):
    if (post.subreddit == "EarthPorn" or
        post.subreddit == "astrophotography" or
        post.subreddit == "backpacking" or
        post.subreddit == "hiking" or
        post.subreddit == "CampingandHiking"):
        return True
    return False

def IsImage(url):
    if (url.endswith('.jpg') or url.endswith('.png')):
        return True
    return False

def Found(url, Data):
    for variable in Data:
        if (variable["url"] == url):
            return True
    return False

def NotPosted(url):
    JsonFile = open("Posted.json", "r")
    PostedData = json.load(JsonFile)
    JsonFile.close()
    if(not Found(url, PostedData)):
        PostedData.append({"Id": PostedData[-1]["Id"]+1, "url": url})
        JsonFile = open("Posted.json", "w")
        json.dump(PostedData, JsonFile, indent=4)
        JsonFile.close()
        return True
    return False

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(Configs["TelegramToken"], use_context=True)

    # Get the dispatcher to register handlers
    Dispatcher = updater.dispatcher

    #Get the job queue
    JobQueue = updater.job_queue

    # on different commands - answer in Telegram
    Dispatcher.add_handler(CommandHandler("start", start))
    Dispatcher.add_handler(CommandHandler("help", help))
    Dispatcher.add_handler(CommandHandler("ip", ip))

    # on noncommand i.e message - echo the message on Telegram
    Dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    Dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    job_minute = JobQueue.run_repeating(RedditSender, interval=60, first=0)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()