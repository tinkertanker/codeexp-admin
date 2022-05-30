# noinspection PyPackageRequirements
import discord
import logging


class AdminBot(discord.Bot):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('adminbot')
        self.logger = logger

    def log(self, msg):
        self.logger.info(msg)

    async def on_ready(self):
        self.log(f"Logged in as {self.user}")
