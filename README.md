# Helper bot for https://t.me/django_jobs

- forwards certain messages in Telegram group to a specified channel.
- adds admin commands to help with group management
  - `/warn` - warn a user about job posting requirements
  - `/fw` - manually forward a message to a channel
  - `/ro {3 for flood}` - put user in read-only mode for 1 day. Optionally accepts custom number of days

## Setup

You have to provide several environment variables to be able to run this:

```
BOT_TOKEN=...
FORWARD_FROM_CHAT_ID=...
FORWARD_TO_CHAT_ID=...
CREATOR_ID=...
```

It was created to serve in https://t.me/django_jobs and https://t.me/django_jobs_board
