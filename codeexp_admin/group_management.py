# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands

from codeexp_admin import AdminBot


async def add_groups(ctx: discord.ApplicationContext, category_id: int, num_groups: int = 1):
    def check_is_valid_category(category: discord.CategoryChannel):
        return "category" in category.name.lower()

    def convert_to_id(category: discord.CategoryChannel):
        subcategory = category.name.split(" ")[1]
        cat_num_and_sub = subcategory.split("-")
        return int(cat_num_and_sub[0]), int(cat_num_and_sub[1])

    category_channels = filter(lambda ch: isinstance(ch, discord.CategoryChannel), ctx.guild.channels)

    managed_categories = filter(check_is_valid_category, category_channels)
    managed_channels = map(convert_to_id, managed_categories)
    valid_ids = map(lambda x: x[0], managed_channels)
    if category_id not in valid_ids:
        await ctx.respond(f"Invalid category ID. Valid IDs: {valid_ids}")


class GroupManagement(commands.Cog):
    def __init__(self, bot: AdminBot):
        self.bot = bot

    @commands.slash_command(name="delete_channels", description="Deletes a bunch of channels under some category")
    async def delete_channels(self, ctx: discord.ApplicationContext,
                              category: discord.Option(discord.SlashCommandOptionType.string,
                                                       description="The category name")):
        cat = [x for x in filter(lambda ch: isinstance(ch, discord.CategoryChannel), ctx.guild.channels)]
        wanted_cat = [x for x in cat if x.name.lower() == category.lower()]
        if not wanted_cat or len(list(wanted_cat)) < 1:
            await ctx.respond("No category found", ephemeral=True)
            return
        wanted_cat = list(wanted_cat)[0]
        channels = wanted_cat.channels
        msg = await ctx.respond("Working now...", ephemeral=True)
        with ctx.typing():
            for channel in channels:
                await channel.delete()
                await msg.edit_original_message(content=f"Deleted {channel.name}")
        await msg.edit_original_message(content="Done")

    @commands.slash_command(name="create_group", description="Creates a group")
    async def create_group(self, ctx: discord.ApplicationContext,
                           category_id: discord.Option(choices=['0', '1'], description="The category ID"),
                           num_groups: discord.Option(discord.SlashCommandOptionType.integer,
                                                      "The number of groups to create")):

        category_channels = filter(lambda channel: isinstance(channel, discord.CategoryChannel), ctx.guild.channels)

        await ctx.respond([str(c) for c in category_channels], ephemeral=True)
        await add_groups(ctx, category_id, num_groups)
        return
        if not isinstance(cat, discord.CategoryChannel):
            await ctx.respond("Weird bug (not a category channel)", ephemeral=True)
            return
        if num_groups and num_groups < 2:
            await ctx.respond("Does not make sense", ephemeral=True)
            return
        if not num_groups:
            num_groups = 1

        status_msg = await ctx.respond("Working", ephemeral=True)

        channel_nums = [int(chan.name.split("-")[-1]) for chan in cat.channels]
        last_channel = 0
        if len(channel_nums) >= 50:
            self.bot.log("Too many channels in the category")
            await status_msg.edit_original_message(content="Cannot do this, too many channels in this category")
            return
        if len(channel_nums) > 0:
            last_channel = sorted(channel_nums)[-1]

        for x in range(1, num_groups + 1):
            await cat.create_text_channel(f"group-{last_channel + x}")
            await cat.create_voice_channel(f"group-voice-{last_channel + x}")
            await status_msg.edit_original_message(content=f"Working on group {last_channel + x}")


def setup(bot: AdminBot):
    bot.add_cog(GroupManagement(bot))
