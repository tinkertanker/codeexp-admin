# Contributing

Thank you for contributing to the CODE_EXP admin bot.

## Development environment setup

Clone the bot, then run `pip install -r requirements.txt`. You will need several environment variables defined. Here is the `.env` file template you can use

```
DISCORD_TOKEN=<your token here>
GUILD_ID=<guild id here>
MENTOR_ROLE_ID=<mentor role id here>
MEMBER_ROLE_ID<member role id>
SENTRY_DSN=<sentry dsn>
```

We use Sentry for error handling. However, the bot will start without a sentry DSN.


## Making a pull request.

Please @ the maintainers of this repository if you would like your pull request to be reviewed. Please try your best to explain
any changes you have made. We may request for additional changes to be made. Please do your best to work on them.

If you have made many commits, please rebase and squash all your commits into 1 when the maintainer asks you to do so.

