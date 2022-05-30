# noinspection PyPackageRequirements
import discord
import logging


class AdminBot(discord.Bot):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

    def _setup_logging(self):
        pass