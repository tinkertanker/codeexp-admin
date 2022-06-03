# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands

from codeexp_admin import AdminBot


class EventHandlers(commands.Cog):

    def __init__(self, bot: AdminBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id != self.bot.debug_guilds[0]:
            return
        dm = await member.create_dm()
        if member.name.lower().startswith("dsta mentor"):
            await member.add_roles(member.guild.get_role(self.bot.cfg.mentor_role))
            await dm.send(f"Welcome, {member.mention}! You have been assigned to the mentor role.")


def setup(bot: AdminBot):
    bot.add_cog(EventHandlers(bot))
