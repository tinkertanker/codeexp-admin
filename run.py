from dotenv import load_dotenv

from codeexp_admin import AdminBot, Config

import logging
import os


def main():
    load_dotenv()
    logger = logging.getLogger("pre-run")
    if not os.getenv("DISCORD_TOKEN"):
        logger.error("DISCORD_TOKEN environment variable not set")
        return
    if not os.getenv("GUILD_ID"):
        logger.error("GUILD_ID environment variable not set")
        return

    if not os.getenv("MENTOR_ROLE_ID"):
        logger.error("MENTOR_ROLE_ID environment variable not set")
        return

    if not os.getenv("SENTRY_DSN"):
        logger.warning("Not running with sentry. You won't have easy access to error reports. Continuing anyway...")

    conf = Config(token=os.getenv("DISCORD_TOKEN"), guild=int(os.getenv("GUILD_ID")),
                  mentor_role=int(os.getenv("MENTOR_ROLE_ID")), sentry_dsn=os.getenv("SENTRY_DSN"))

    bot = AdminBot(conf)
    bot.run(conf.token)


if __name__ == "__main__":
    main()
