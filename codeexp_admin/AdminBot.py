import os
from collections import namedtuple

# noinspection PyPackageRequirements
import discord
import logging

from codeexp_admin.sqlite_engine import SqliteEngine

Config = namedtuple("Config", ["token", "guild"])


class AdminBot(discord.Bot):
    def __init__(self, conf: Config, *args, **options):
        intents = discord.Intents.default()
        # noinspection PyDunderSlots, PyUnresolvedReferences
        intents.members = True
        super().__init__(debug_guilds=[conf.guild], intents=intents, *args, **options)
        self.cfg = conf
        self._setup_logging()
        self.sqlite_engine = SqliteEngine(os.path.join(os.path.dirname(__file__), "..", "data.db"))
        self.sqlite_engine.exec_file(os.path.join(os.path.dirname(__file__), "..", "db.sql"))

        self.load_extension("codeexp_admin.group_management")

    def _setup_logging(self):
        logging.basicConfig()
        logger = logging.getLogger('adminbot')
        logger.setLevel(logging.INFO)
        self.logger = logger

    def log(self, msg):
        self.logger.info(msg)

    async def on_ready(self):
        self.log(f"Logged in as {self.user}")
