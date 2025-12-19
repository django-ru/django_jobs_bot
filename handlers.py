import os
import time

from telegram import ChatPermissions, ParseMode, Update
from telegram.ext import MessageHandler, CommandHandler, CallbackContext

from bot import logger
from filters import with_default_filters
from utils import plural_days


def log_errors(update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def log_excluded_message_callback(update: Update, context: CallbackContext):
    """Log messages that didn't match auto-forward criteria."""
    from filters import contains_job_hashtag, contains_django_mention

    msg = update.message
    if not msg or not (msg.text or msg.caption):
        return

    user = msg.from_user
    text = (msg.text or msg.caption or "").lower()
    has_job_tag = contains_job_hashtag.filter(msg)
    has_django = contains_django_mention.filter(msg)

    # Only log if message partially matches (to reduce noise)
    if has_job_tag or has_django:
        text_preview = (msg.text or msg.caption or "")[:50]
        logger.info(
            "EXCLUDED: msg_id=%s from_user=%s (@%s) has_job=%s has_django=%s preview='%s...'",
            msg.message_id,
            user.id,
            user.username or "no_username",
            has_job_tag,
            has_django,
            text_preview,
        )


# callbacks


def auto_forward_callback(update: Update, context: CallbackContext):
    chat_id_to_forward = int(os.getenv("CHAT_ID_TO"))
    user = update.message.from_user
    text_preview = (update.message.text or update.message.caption or "")[:50]
    logger.info(
        "AUTO-FORWARD: msg_id=%s from_user=%s (@%s) to_chat=%s preview='%s...'",
        update.message.message_id,
        user.id,
        user.username or "no_username",
        chat_id_to_forward,
        text_preview,
    )
    update.message.forward(chat_id=chat_id_to_forward)


def manual_forward_callback(update: Update, context: CallbackContext):
    chat_id_to_forward = int(os.getenv("CHAT_ID_TO"))
    admin = update.message.from_user
    target_msg = update.message.reply_to_message
    target_user = target_msg.from_user
    text_preview = (target_msg.text or target_msg.caption or "")[:50]
    logger.info(
        "MANUAL-FORWARD: admin=@%s target_msg_id=%s target_user=%s (@%s) to_chat=%s preview='%s...'",
        admin.username,
        target_msg.message_id,
        target_user.id,
        target_user.username or "no_username",
        chat_id_to_forward,
        text_preview,
    )
    target_msg.forward(chat_id=chat_id_to_forward)
    update.message.delete()


def warn_callback(update: Update, context: CallbackContext):
    rules_url = os.getenv("RULES_URL")
    admin = update.message.from_user
    target_user = update.message.reply_to_message.from_user
    logger.info(
        "WARN: admin=@%s target_user=%s (@%s) msg_id=%s",
        admin.username,
        target_user.id,
        target_user.username or "no_username",
        update.message.reply_to_message.message_id,
    )
    message = (
        f"Привет! У нас есть [правила оформления вакансий и резюме]({rules_url}). "
        f"Отредактируйте ваше сообщение и оно отправится в канал @django\\_jobs\\_board."
    )
    update.message.reply_to_message.reply_text(
        text=message, parse_mode=ParseMode.MARKDOWN, quote=True
    )
    update.message.delete()


def readonly_callback(update: Update, context: CallbackContext):
    admin = update.message.from_user
    user = update.message.reply_to_message.from_user
    days, reason = update.message.text.strip("/ro ").split(" ", 1)
    if days.isnumeric():
        days = int(days)
    else:
        days = 1
    seconds = days * 24 * 60 * 60

    logger.info(
        "READONLY: admin=@%s target_user=%s (@%s) duration=%s_days reason='%s'",
        admin.username,
        user.id,
        user.username or "no_username",
        days,
        reason or "none",
    )

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
    update.message.reply_to_message.reply_text(
        text=message, parse_mode=ParseMode.MARKDOWN, quote=True
    )
    update.message.delete()


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


def log_excluded_messages(*filters) -> MessageHandler:
    """Handler to log messages that don't match auto-forward criteria."""
    return MessageHandler(
        filters=with_default_filters(*filters), callback=log_excluded_message_callback
    )
