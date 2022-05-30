# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands

from codeexp_admin import AdminBot


class GroupManagement(commands.Cog):
    def __init__(self, bot: AdminBot):
        self.bot = bot

    @commands.slash_command(name="create_group", description="Creates a group")
    async def create_group(self, ctx: discord.ApplicationContext,
                           category_id: discord.Option(choices=['0', '1'], description="The category ID"),
                           num_groups: discord.Option(discord.SlashCommandOptionType.integer,
                                                      "The number of groups to create")):
        # TODO: remove this hardcoded nonsense
        lookup_table = {'0': 980734245381222400, '1': 980735809848238131}
        cat = self.bot.get_channel(lookup_table[category_id])
        if not isinstance(cat, discord.CategoryChannel):
            await ctx.respond("Weird bug (not a category channel)", ephemeral=True)
            return
        if num_groups and num_groups < 2:
            await ctx.respond("Does not make sense", ephemeral=True)
            return
        if not num_groups:
            num_groups = 1

        channel_nums = [int(chan.name.split("-")[-1]) for chan in cat.channels]
        last_channel = 0
        if len(channel_nums) > 0:
            last_channel = sorted(channel_nums)[-1]

        status_msg = await ctx.respond("Working", ephemeral=True)

        for x in range(1, num_groups + 1):
            await cat.create_text_channel(f"group-{last_channel + x}")
            await cat.create_voice_channel(f"group-voice-{last_channel + x}")
            await status_msg.edit(content=f"Working on group {last_channel + x}")


def setup(bot: AdminBot):
    bot.add_cog(GroupManagement(bot))
