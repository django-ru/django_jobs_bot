import logging
import os

from telegram.ext import filters as ext_filters, ApplicationBuilder

import filters
import handlers
from utils import in_heroku, init_sentry, in_render

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    bot_token = os.getenv("BOT_TOKEN")
    admins = os.getenv("ADMINS", "").split(",")

    application = ApplicationBuilder().token(bot_token).build()

    # automated message forwarding
    application.add_handler(
        handlers.auto_forward_messages(
            ext_filters.TEXT,
            ext_filters.UpdateType.MESSAGE,
            ~ext_filters.COMMAND,
            filters.contains_job_hashtag,
            filters.contains_django_mention,
        )
    )
    # manual admin commands
    application.add_handler(
        handlers.reply_warning_to_messages(
            ext_filters.REPLY,
            ext_filters.COMMAND,
            ext_filters.User(username=admins),
        )
    )
    application.add_handler(
        handlers.manual_forward_messages(
            ext_filters.REPLY,
            ext_filters.COMMAND,
            ext_filters.User(username=admins),
            filters.forwarded_message_contains_job_hashtag,
            filters.forwarded_message_contains_django_mention,
        )
    )
    application.add_handler(
        handlers.put_in_readonly_for_message(
            ext_filters.REPLY,
            ext_filters.COMMAND,
            ext_filters.User(username=admins),
        )
    )
    # error handling
    application.add_error_handler(handlers.log_errors)

    if in_heroku():
        app_name = os.getenv("HEROKU_APP_NAME")
        init_sentry()
        application.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT")),
            url_path=bot_token,
            webhook_url=f"https://{app_name}.herokuapp.com/" + bot_token,
        )
    elif in_render():
        app_name = os.getenv("RENDER_APP_NAME")
        init_sentry()
        application.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT")),
            url_path=bot_token,
            webhook_url=f"https://{app_name}.onrender.com/" + bot_token,
        )
    else:
        application.run_polling()
