# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands

from codeexp_admin import AdminBot
from codeexp_admin.chan_mgmt import create_managed_channels, delete_managed_channels


class GroupManagement(commands.Cog):
    def __init__(self, bot: AdminBot):
        self.bot = bot

    @commands.slash_command(name="delete_all", description="Deletes all managed channels in a category")
    async def delete_all(self, ctx: discord.ApplicationContext,
                         category_id: discord.Option(choices=['0', '1'], description="Category ID")):
        update_msg = await ctx.respond("Now working...", ephemeral=True)
        await delete_managed_channels(ctx.guild, int(category_id), update_message=update_msg)
        await update_msg.edit_original_message(content=f"Deleted all managed channels in category {category_id}")

    @commands.slash_command(name="create_group", description="Creates a group")
    async def create_group(self, ctx: discord.ApplicationContext,
                           category_id: discord.Option(choices=['0', '1'], description="The category ID"),
                           num_groups: discord.Option(discord.SlashCommandOptionType.integer,
                                                      "The number of groups to create")):

        if num_groups and num_groups < 2:
            await ctx.respond("Does not make sense", ephemeral=True)
            return
        if not num_groups:
            num_groups = 1
        update_msg = await ctx.respond("Now working...", ephemeral=True)
        await create_managed_channels(ctx.guild, int(category_id), num_groups, update_message=update_msg)




def setup(bot: AdminBot):
    bot.add_cog(GroupManagement(bot))
