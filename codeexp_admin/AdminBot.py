import os
from collections import namedtuple

# noinspection PyPackageRequirements
import discord
import logging

from discord.ext import bridge

import sentry_sdk

from codeexp_admin.sqlite_engine import SqliteEngine

Config = namedtuple("Config", ["token", "guild", "mentor_role", "sentry_dsn", "member_role"])


class AdminBot(bridge.Bot):
    def __init__(self, conf: Config, *args, **options):
        intents = discord.Intents.default()
        # noinspection PyDunderSlots, PyUnresolvedReferences
        intents.members = True
        super().__init__(debug_guilds=[conf.guild], intents=intents, command_prefix="!", *args, **options)
        self.cfg = conf
        self._setup_logging()
        self._setup_sentry()
        self.sqlite_engine = SqliteEngine(os.path.join(os.path.dirname(__file__), "..", "data.db"))
        self.sqlite_engine.exec_file(os.path.join(os.path.dirname(__file__), "..", "db.sql"))

        self.load_extension("codeexp_admin.cogs.group_management")
        self.load_extension("codeexp_admin.cogs.user_autoassignment")
        self.load_extension("codeexp_admin.cogs.events")

    def _setup_logging(self):
        logging.basicConfig()
        logger = logging.getLogger('adminbot')
        logger.setLevel(logging.INFO)
        self.logger = logger

    def _setup_sentry(self):
        if self.cfg.sentry_dsn:
            sentry_sdk.init(self.cfg.sentry_dsn, traces_sample_rate=0.5)

    def log(self, msg):
        self.logger.info(msg)

    async def on_ready(self):
        self.log(f"Logged in as {self.user}")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                             name="for infractions"))
