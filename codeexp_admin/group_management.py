# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands

from codeexp_admin import AdminBot


def get_categories(guild: discord.Guild) -> list[discord.CategoryChannel]:
    category_channels = filter(lambda chan: isinstance(chan, discord.CategoryChannel), guild.channels)
    return list(category_channels)


def get_managed_category_channels(guild: discord.Guild) -> list[discord.CategoryChannel]:
    category_channels = get_categories(guild)

    def check_is_valid_category(category: discord.CategoryChannel):
        return "category" in category.name.lower()

    managed_categories = filter(check_is_valid_category, category_channels)
    return list(managed_categories)


def get_managed_channel_ids(guild: discord.Guild) -> list[tuple[int, int, discord.CategoryChannel]]:
    def convert_to_id(category: discord.CategoryChannel):
        subcategory = category.name.split(" ")[1]
        cat_num_and_sub = subcategory.split("-")
        return int(cat_num_and_sub[0]), int(cat_num_and_sub[1]), category

    managed_channels = get_managed_category_channels(guild)
    return list(map(convert_to_id, managed_channels))


def build_managed_categories_lookup_table(managed_channels: list[tuple[int, int, discord.CategoryChannel]]) -> dict:
    lookup_table = {}
    for (cat_num, subcat_num, chan) in managed_channels:
        if cat_num not in lookup_table:
            lookup_table[cat_num] = []
        lookup_table[cat_num].append((subcat_num, chan))
    return lookup_table


async def add_groups(ctx: discord.ApplicationContext, category_id: int, num_groups: int = 1):
    sub_ids = build_managed_categories_lookup_table(get_managed_channel_ids(ctx.guild))
    if category_id not in [*sub_ids.keys()]:
        await ctx.respond(f"Invalid category ID. Valid IDs: {[*sub_ids.keys()]}", ephemeral=True)
        return
    # await ctx.respond(sub_ids, ephmeral=True)
    status_msg = await ctx.respond("Working", ephemeral=True)


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

        if num_groups and num_groups < 2:
            await ctx.respond("Does not make sense", ephemeral=True)
            return
        if not num_groups:
            num_groups = 1

        await add_groups(ctx, int(category_id), num_groups)


def setup(bot: AdminBot):
    bot.add_cog(GroupManagement(bot))
