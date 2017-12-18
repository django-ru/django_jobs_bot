import logging
import os

from telegram.ext import Updater, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
CREATOR_ID = os.environ.get('CREATOR_ID')
TAGS_TO_FORWARD = ['#cv', '#job', '#вакансия', '#работа']


def forward_message(bot, update):
    if any([tag in update.message.text for tag in TAGS_TO_FORWARD]):
        forward_to = CHAT_ID
    else:
        forward_to = CREATOR_ID

    logger.warning('Forwarding message to %s', forward_to)
    bot.forward_message(
        chat_id=forward_to,
        from_chat_id=update.message.chat.id,
        message_id=update.message.message_id
    )


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def start_bot():
    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError('BOT_TOKEN or CHAT_ID missing from environment variables')

    updater = Updater(BOT_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, forward_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start_bot()
