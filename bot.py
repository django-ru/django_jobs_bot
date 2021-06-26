import logging
import operator
import os
from functools import reduce

import sentry_sdk
from telegram import Message, Update
from telegram.ext import CallbackContext, MessageHandler, Updater
from telegram.ext.filters import MessageFilter, Filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def forward(update: Update, context: CallbackContext):
    chat_id_to_forward = int(os.getenv("CHAT_ID_TO"))
    logger.info("Forwarding message to %s", chat_id_to_forward)
    update.message.forward(chat_id=chat_id_to_forward)


def log_errors(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


class ContainsJobHashTag(MessageFilter):
    JOB_HASHTAGS = ["#cv", "#job", "#вакансия", "#работа"]

    def filter(self, message: Message) -> bool:
        return any([tag in message.text.lower() for tag in self.JOB_HASHTAGS])


def with_default_filters(*filters):
    """Apply default filters to the given filter classes"""
    default_filters = [
        Filters.text,
        Filters.chat(
            chat_id=int(os.getenv("CHAT_ID_FROM")),
        ),
    ]
    return reduce(operator.and_, [*default_filters, *filters])


def forward_messages_that_match(*filters) -> MessageHandler:
    return MessageHandler(filters=with_default_filters(*filters), callback=forward)


def in_heroku() -> bool:
    return os.getenv("HEROKU_APP_NAME") is not None


def init_sentry():
    sentry_dsn = os.getenv("SENTRY_DSN")

    if sentry_dsn:
        sentry_sdk.init(sentry_dsn)


def main():
    bot_token = os.getenv("BOT_TOKEN")

    bot = Updater(bot_token)
    bot.dispatcher.add_handler(forward_messages_that_match(ContainsJobHashTag))
    bot.dispatcher.add_error_handler(log_errors)

    if in_heroku():
        app_name = os.getenv("HEROKU_APP_NAME")
        init_sentry()
        bot.start_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT", 5000)),
            url_path=bot_token,
            webhook_url=f"https://{app_name}.herokuapp.com/" + bot_token,
        )
        bot.idle()
    else:
        bot.start_polling()


if __name__ == "__main__":
    main()
