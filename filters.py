import logging
import operator
import os
from functools import reduce

from telegram import Message
from telegram.ext import MessageFilter, Filters

logger = logging.getLogger(__name__)


def with_default_filters(*filters):
    """Apply default filters to the given filter classes."""
    default_filters = [
        Filters.chat(
            chat_id=int(os.getenv("CHAT_ID_FROM")),
        ),
    ]
    return reduce(operator.and_, [*default_filters, *filters])


class _ContainsJobHashTag(MessageFilter):
    JOB_HASHTAGS = ["#cv", "#job"]

    def filter(self, message: Message) -> bool:
        text = (message.text or message.caption or "").lower()
        result = any([tag in text for tag in self.JOB_HASHTAGS])
        if result:
            found_tags = [tag for tag in self.JOB_HASHTAGS if tag in text]
            logger.debug(
                "Message %s contains job hashtag(s): %s",
                message.message_id,
                ", ".join(found_tags),
            )
        return result


class _ContainsDjangoMention(MessageFilter):
    def filter(self, message: Message) -> bool:
        text = (message.text or message.caption or "").lower()
        result = "django" in text
        if result:
            logger.debug("Message %s contains django mention", message.message_id)
        return result


class _ForwardedMessageContainsJobHashTag(MessageFilter):
    JOB_HASHTAGS = ["#cv", "#job"]

    def filter(self, message: Message) -> bool:
        return contains_job_hashtag.filter(message.reply_to_message)


class _ForwardedMessageContainsDjangoMention(MessageFilter):
    def filter(self, message: Message) -> bool:
        return contains_django_mention.filter(message.reply_to_message)


contains_job_hashtag = _ContainsJobHashTag()
contains_django_mention = _ContainsDjangoMention()
forwarded_message_contains_job_hashtag = _ForwardedMessageContainsJobHashTag()
forwarded_message_contains_django_mention = _ForwardedMessageContainsDjangoMention()
