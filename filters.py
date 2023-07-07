import operator
import os
from functools import reduce

from telegram import Message
from telegram.ext import filters as ext_filters


def with_default_filters(*filters):
    """Apply default filters to the given filter classes."""
    default_filters = [
        ext_filters.Chat(
            chat_id=int(os.getenv("CHAT_ID_FROM")),
        ),
    ]
    return reduce(operator.and_, [*default_filters, *filters])


class _ContainsJobHashTag(ext_filters.MessageFilter):
    JOB_HASHTAGS = ["#cv", "#job"]

    def filter(self, message: Message) -> bool:
        return any([tag in message.text.lower() for tag in self.JOB_HASHTAGS])


class _ContainsDjangoMention(ext_filters.MessageFilter):
    def filter(self, message: Message) -> bool:
        return "django" in message.text.lower()


class _ForwardedMessageContainsJobHashTag(ext_filters.MessageFilter):
    JOB_HASHTAGS = ["#cv", "#job"]

    def filter(self, message: Message) -> bool:
        return contains_job_hashtag.filter(message.reply_to_message)


class _ForwardedMessageContainsDjangoMention(ext_filters.MessageFilter):
    def filter(self, message: Message) -> bool:
        return contains_django_mention.filter(message.reply_to_message)


contains_job_hashtag = _ContainsJobHashTag()
contains_django_mention = _ContainsDjangoMention()
forwarded_message_contains_job_hashtag = _ForwardedMessageContainsJobHashTag()
forwarded_message_contains_django_mention = _ForwardedMessageContainsDjangoMention()
