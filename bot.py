import logging
import os

from telegram.ext import Updater, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
FORWARD_FROM_CHAT_ID = os.environ.get('FORWARD_FROM_CHAT_ID')
FORWARD_TO_CHAT_ID = os.environ.get('FORWARD_TO_CHAT_ID')
CREATOR_ID = os.environ.get('CREATOR_ID')
BOT_POLL_INTERVAL = os.environ.get('BOT_POLL_INTERVAL', 3600)
TAGS_TO_FORWARD = ['#cv', '#job', '#вакансия', '#работа']

SOCKS_URL = os.environ.get('SOCKS_URL')
SOCKS_USER = os.environ.get('SOCKS_USER')
SOCKS_PASSWORD = os.environ.get('SOCKS_PASSWORD')


def forward_message(bot, update):
    if str(update.message.chat.id) != FORWARD_FROM_CHAT_ID:
        logger.warning('Blocked attempt to forward from %s', update.message.chat.id)
        return
    if any([tag in update.message.text.lower() for tag in TAGS_TO_FORWARD]):
        forward_to = FORWARD_TO_CHAT_ID
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
    if not any([BOT_TOKEN, FORWARD_FROM_CHAT_ID, FORWARD_TO_CHAT_ID, CREATOR_ID]):
        raise ValueError(
            'One of the variables -'
            'BOT_TOKEN, FORWARD_FROM_CHAT_ID, FORWARD_TO_CHAT_ID or CREATOR_ID'
            'is missing in environment'
        )

    if SOCKS_URL:
        proxy_config = {
            'proxy_url': SOCKS_URL,
            'urllib3_proxy_kwargs': {'username': SOCKS_USER, 'password': SOCKS_PASSWORD}
        }
    else:
        proxy_config = None
    updater = Updater(BOT_TOKEN, request_kwargs=proxy_config)

    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, forward_message))
    dp.add_error_handler(error)

    logger.info('Start polling...')
    updater.start_polling(poll_interval=float(BOT_POLL_INTERVAL))
    updater.idle()


if __name__ == '__main__':
    start_bot()
