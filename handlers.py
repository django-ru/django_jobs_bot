import os
import time

from telegram import ChatPermissions, Update
from telegram.constants import ParseMode
from telegram.ext import MessageHandler, CommandHandler, ContextTypes

from bot import logger
from filters import with_default_filters
from utils import plural_days


def log_errors(update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


# callbacks


async def auto_forward_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id_to_forward = int(os.getenv("CHAT_ID_TO"))
    logger.info(
        "Forwarding message %s to %s", update.message.message_id, chat_id_to_forward
    )
    await update.message.forward(chat_id=chat_id_to_forward)


async def manual_forward_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id_to_forward = int(os.getenv("CHAT_ID_TO"))
    logger.info(
        "Forwarding message %s to %s", update.message.message_id, chat_id_to_forward
    )
    await update.message.reply_to_message.forward(chat_id=chat_id_to_forward)
    await update.message.delete()


async def warn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules_url = os.getenv("RULES_URL")
    message = (
        f"Привет! У нас есть [правила оформления вакансий и резюме]({rules_url}). "
        f"Отредактируйте ваше сообщение и оно отправится в канал @django\\_jobs\\_board."
    )
    await update.message.reply_to_message.reply_text(
        text=message, parse_mode=ParseMode.MARKDOWN, quote=True
    )
    await update.message.delete()


async def readonly_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.reply_to_message.from_user
    days, reason = update.message.text.strip("/ro ").split(" ", 1)
    if days.isnumeric():
        days = int(days)
    else:
        days = 1
    seconds = days * 24 * 60 * 60

    logger.info("Setting readonly for %s for %s seconds", user.id, seconds)

    context.bot.restrict_chat_member(
        chat_id=update.message.chat_id,
        user_id=user.id,
        permissions=ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
        ),
        until_date=int(time.time() + seconds),
    )

    message = f"{user.name} в ридонли на {days} {plural_days(days)}."
    if reason:
        message += f" по причине: {reason}"
    await update.message.reply_to_message.reply_text(
        text=message, parse_mode=ParseMode.MARKDOWN, quote=True
    )
    await update.message.delete()


# handlers


def auto_forward_messages(*filters) -> MessageHandler:
    return MessageHandler(
        filters=with_default_filters(*filters), callback=auto_forward_callback
    )


def manual_forward_messages(*filters) -> CommandHandler:
    return CommandHandler(
        command="fw",
        filters=with_default_filters(*filters),
        callback=manual_forward_callback,
    )


def reply_warning_to_messages(*filters) -> CommandHandler:
    return CommandHandler(
        command="warn", filters=with_default_filters(*filters), callback=warn_callback
    )


def put_in_readonly_for_message(*filters) -> CommandHandler:
    return CommandHandler(
        command="ro", filters=with_default_filters(*filters), callback=readonly_callback
    )
