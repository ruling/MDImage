# -*- coding: UTF-8 -*-

from uuid import uuid4
from telegram.utils.helpers import escape_markdown
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton,InlineKeyboardMarkup)
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler,\
     InlineQueryHandler,CallbackQueryHandler
import config,logging,DBHelper,OperationStore

#set logging format
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

#auth my bot

#bot start
def start(bot,updater):
    updater.message.reply_text(
        'Hi! I\'m MDImage Bot. I will help you to upload image to qiniu.\n '
        'Send your qiniu ak and sk to me.\n\n'
        'example: /token <xxxxx> <yyyyy> \n'
        'x is you ak,y is you sk',)

def token(bot,updater,args,chat_data):
    user = updater.message.from_user
    #check whether user exist in db,if not then insert else update data
    if DBHelper.getData(user.username) == False:
        insetResult = DBHelper.insertData(user.username,args[0],args[1],args[2])
        if insetResult:
            updater.message.reply_text('Your account binding success!')
        else:
            updater.message.reply_text('Account binding error,try again later.')
    else:
        updateResult = DBHelper.update(user.username,args[0],args[1],args[2])
        if updateResult:
            updater.message.reply_text('Your info has been updated.')
        else:
            updater.message.reply_text('Sorry,I can\'t update your info,Please check your input')
    reply_markup = chooseBucket(args[0],args[1])
    updater.message.reply_text('Please choose your bucket:',reply_markup=reply_markup)

def photo(bot, updater):
    user = updater.message.from_user
    photo_file = bot.get_file(updater.message.photo[-1].file_id)
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    updater.message.reply_text('Gorgeous! Now, send me your location please, '
                              'or send /skip if you don\'t want to.')

def chooseBucket(ak,sk):
    bukcets = OperationStore.getBucketList(ak,sk)
    logger.info("buckets is %s",bukcets)
    #create inlinekeyboard data
    keyboard = []
    for bukcet in bukcets:
        keyboard.append([InlineKeyboardButton(bukcet,callback_data=bukcet)])
    #rely to user
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def cancel(bot, updater):
    user = updater.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    updater.message.reply_text('Bye! I hope we can talk again some day.')

    return ConversationHandler.END

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    updater = Updater(token=config.BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start',start))
    dispatcher.add_handler(MessageHandler(Filters.photo, photo))
    dispatcher.add_handler(CommandHandler('token',token,pass_args=True,pass_chat_data=True))
   # dispatcher.add_handler(CommandHandler('choose',chooseBucket))
    dispatcher.add_handler(CommandHandler('cancel',cancel))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()