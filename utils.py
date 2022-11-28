import os

import sentry_sdk


def in_heroku() -> bool:
    return os.getenv("HEROKU_APP_NAME") is not None


def in_render() -> bool:
    return os.getenv("RENDER_APP_NAME") is not None


def init_sentry():
    sentry_dsn = os.getenv("SENTRY_DSN")

    if sentry_dsn:
        sentry_sdk.init(sentry_dsn)


def plural_days(value):
    words = ["день", "дня", "дней"]

    if all((value % 10 == 1, value % 100 != 11)):
        return words[0]
    elif all((2 <= value % 10 <= 4, any((value % 100 < 10, value % 100 >= 20)))):
        return words[1]
    return words[2]
