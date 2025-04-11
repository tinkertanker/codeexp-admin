# noinspection PyPackageRequirements
import discord

# noinspection PyPackageRequirements
from discord.ext import commands

from codeexp_admin import AdminBot
from codeexp_admin.chan_mgmt import create_managed_channels, delete_managed_channels


class GroupManagement(commands.Cog):
    def __init__(self, bot: AdminBot):
        self.bot = bot

    @commands.slash_command(
        name="delete_discord_category",
        description="Deletes all groups in some DISCORD category",
    )
    @commands.has_permissions(manage_channels=True)
    async def delete_all_groups_in_category(
        self,
        ctx: discord.ApplicationContext,
        category: discord.Option(
            discord.SlashCommandOptionType.string, description="The category name"
        ),
    ):
        await ctx.respond("Currently disabled", ephemeral=True)
        # cat = [x for x in filter(lambda ch: isinstance(ch,
        # discord.CategoryChannel), ctx.guild.channels)]
        # wanted_cat = [x for x in cat if x.name.lower() == category.lower()]
        # if not wanted_cat or len(list(wanted_cat)) < 1:
        #     await ctx.respond("No category found", ephemeral=True)
        #     return
        # wanted_cat = list(wanted_cat)[0]
        # channels = wanted_cat.channels
        # msg = await ctx.respond("Working now...", ephemeral=True)
        # with ctx.typing():
        #     for channel in channels:
        #         await channel.delete()
        #         await msg.edit_original_message(content=f"Deleted {channel.name}")
        # await msg.edit_original_message(content="Done")

    @commands.slash_command(
        name="delete_all", description="Deletes all managed channels in a category"
    )
    @commands.has_permissions(manage_channels=True)
    async def delete_all(
        self,
        ctx: discord.ApplicationContext,
        category_id: discord.Option(choices=["1", "2"], description="Category ID"),
    ):
        update_msg = await ctx.respond("Now working...", ephemeral=True)
        await delete_managed_channels(
            ctx.guild,
            int(category_id),
            update_message=update_msg,
            engine=self.bot.sqlite_engine,
        )
        await update_msg.edit_original_message(
            content=f"Deleted all managed channels in category {category_id}"
        )

    @commands.slash_command(name="create_group", description="Creates a group")
    @commands.has_permissions(manage_channels=True)
    async def create_group(
        self,
        ctx: discord.ApplicationContext,
        category_id: discord.Option(
            choices=["1", "2"],
            # TODO: do not hardcode choices
            description="The category ID",
        ),
        num_groups: discord.Option(
            discord.SlashCommandOptionType.integer, "The number of groups to create"
        )
    ):

        if num_groups < 1:
            await ctx.respond("Does not make sense", ephemeral=True)
            return
        update_msg = await ctx.respond("Now working...", ephemeral=True)
        await create_managed_channels(
            ctx.guild,
            int(category_id),
            num_groups,
            update_message=update_msg,
            engine=self.bot.sqlite_engine,
        )

    @commands.Cog.listener()
    async def on_application_command_error(
        self, ctx: discord.ApplicationContext, error: Exception
    ):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond(str(error), ephemeral=True)
            return
        await ctx.respond(
            "An error occurred, please contact the developer", ephemeral=True
        )


def setup(bot: AdminBot):
    bot.add_cog(GroupManagement(bot))
