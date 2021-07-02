import logging
import operator
import os
from functools import reduce

import sentry_sdk
from telegram import Message, ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Updater
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


def warn(update: Update, context: CallbackContext):
    rules_url = os.getenv("RULES_URL")
    message = f"Привет! У нас есть [правила оформления вакансий и резюме]({rules_url}). " \
              f"Отредактируйте ваше сообщение и оно будет отправлено в канал @django\\_jobs\\_board."
    update.message.reply_to_message.reply_text(
        text=message, parse_mode=ParseMode.MARKDOWN, quote=True
    )
    update.message.delete()


def log_errors(update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


class ContainsJobHashTag(MessageFilter):
    JOB_HASHTAGS = ["#cv", "#job"]

    def filter(self, message: Message) -> bool:
        return any([tag in message.text.lower() for tag in self.JOB_HASHTAGS])


def with_default_filters(*filters):
    """Apply default filters to the given filter classes."""
    default_filters = [
        Filters.chat(
            chat_id=int(os.getenv("CHAT_ID_FROM")),
        ),
    ]
    return reduce(operator.and_, [*default_filters, *filters])


def forward_messages_that_match(*filters) -> MessageHandler:
    return MessageHandler(filters=with_default_filters(*filters), callback=forward)


def reply_warning_to_messages_that_match(*filters) -> CommandHandler:
    return CommandHandler(
        command="warn", filters=with_default_filters(*filters), callback=warn
    )


def in_heroku() -> bool:
    return os.getenv("HEROKU_APP_NAME") is not None


def init_sentry():
    sentry_dsn = os.getenv("SENTRY_DSN")

    if sentry_dsn:
        sentry_sdk.init(sentry_dsn)


def main():
    bot_token = os.getenv("BOT_TOKEN")
    admins = os.getenv("ADMINS").split(",")

    bot = Updater(bot_token)
    bot.dispatcher.add_handler(
        forward_messages_that_match(
            ContainsJobHashTag(),
            Filters.text,
            ~Filters.command,
        )
    )
    bot.dispatcher.add_handler(
        reply_warning_to_messages_that_match(
            Filters.reply, Filters.command, Filters.user(username=admins)
        )
    )
    bot.dispatcher.add_error_handler(log_errors)

    if in_heroku():
        app_name = os.getenv("HEROKU_APP_NAME")
        init_sentry()
        bot.start_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT")),
            url_path=bot_token,
            webhook_url=f"https://{app_name}.herokuapp.com/" + bot_token,
        )
        bot.idle()
    else:
        bot.start_polling()


if __name__ == "__main__":
    main()
