import logging
import os

from telegram.ext import Updater
from telegram.ext.filters import Filters as contrib_filters

import filters
import handlers
from utils import in_heroku, init_sentry, in_render

log_level = logging.DEBUG if os.getenv("DEBUG") else logging.INFO
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=log_level,
)
logger = logging.getLogger(__name__)


def main():
    bot_token = os.getenv("BOT_TOKEN")
    admins = os.getenv("ADMINS", "").split(",")
    chat_id_from = os.getenv("CHAT_ID_FROM")
    chat_id_to = os.getenv("CHAT_ID_TO")

    logger.info("=== Bot Starting ===")
    logger.info("Monitoring chat: %s", chat_id_from)
    logger.info("Forwarding to: %s", chat_id_to)
    logger.info("Admins: %s", ", ".join(admins))

    bot = Updater(bot_token)
    # automated message forwarding
    bot.dispatcher.add_handler(
        handlers.auto_forward_messages(
            contrib_filters.text | contrib_filters.caption,
            contrib_filters.update.message,
            ~contrib_filters.command,
            filters.contains_job_hashtag,
            filters.contains_django_mention,
        )
    )
    # log excluded messages (must be after auto_forward to catch non-matches)
    bot.dispatcher.add_handler(
        handlers.log_excluded_messages(
            contrib_filters.text | contrib_filters.caption,
            contrib_filters.update.message,
            ~contrib_filters.command,
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
        logger.info("Mode: Heroku webhook (%s)", app_name)
        bot.start_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT")),
            url_path=bot_token,
            webhook_url=f"https://{app_name}.herokuapp.com/" + bot_token,
        )
        bot.idle()
    elif in_render():
        app_name = os.getenv("RENDER_APP_NAME")
        init_sentry()
        logger.info("Mode: Render webhook (%s)", app_name)
        bot.start_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT")),
            url_path=bot_token,
            webhook_url=f"https://{app_name}.onrender.com/" + bot_token,
        )
        bot.idle()
    else:
        logger.info("Mode: Polling")
        bot.start_polling()


if __name__ == "__main__":
    main()
