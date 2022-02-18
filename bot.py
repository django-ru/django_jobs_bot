import logging
import os

from telegram.ext import Updater
from telegram.ext.filters import Filters as contrib_filters

import filters
import handlers
from utils import in_heroku, init_sentry

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    bot_token = os.getenv("BOT_TOKEN")
    admins = os.getenv("ADMINS").split(",")

    bot = Updater(bot_token)
    # automated message forwarding
    bot.dispatcher.add_handler(
        handlers.auto_forward_messages(
            contrib_filters.text,
            contrib_filters.update.message,
            ~contrib_filters.command,
            filters.contains_job_hashtag,
            filters.contains_django_mention,
        )
    )
    # manual admin commands
    bot.dispatcher.add_handler(
        handlers.reply_warning_to_messages(
            contrib_filters.reply,
            contrib_filters.command,
            contrib_filters.user(username=admins),
        )
    )
    bot.dispatcher.add_handler(
        handlers.manual_forward_messages(
            contrib_filters.reply,
            contrib_filters.command,
            contrib_filters.user(username=admins),
            filters.forwarded_message_contains_job_hashtag,
            filters.forwarded_message_contains_django_mention,
        )
    )
    bot.dispatcher.add_handler(
        handlers.put_in_readonly_for_message(
            contrib_filters.reply,
            contrib_filters.command,
            contrib_filters.user(username=admins),
        )
    )
    # error handling
    bot.dispatcher.add_error_handler(handlers.log_errors)

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
