# Forwarding bot for https://t.me/django_jobs

Stupidly simple bot that forwards group messages with certain hashtags to specified Telegram channel.

You have to provide several environment variables to be able to run this:

```
BOT_TOKEN=...
FORWARD_FROM_CHAT_ID=...
FORWARD_TO_CHAT_ID=...
CREATOR_ID=...
```

It was created to serve in https://t.me/django_jobs and https://t.me/django_jobs_board
