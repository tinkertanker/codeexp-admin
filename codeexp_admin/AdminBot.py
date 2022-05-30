from collections import namedtuple

# noinspection PyPackageRequirements
import discord
import logging

Config = namedtuple("Config", ["token", "guild"])


class AdminBot(discord.Bot):
    def __init__(self, conf: Config, *args, **options):
        intents = discord.Intents.default()
        # noinspection PyDunderSlots, PyUnresolvedReferences
        intents.members = True
        super().__init__(debug_guilds=[conf.guild], intents=intents, *args, **options)
        self.cfg = conf
        self._setup_logging()

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
