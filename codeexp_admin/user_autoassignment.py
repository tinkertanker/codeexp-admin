# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands

from codeexp_admin import AdminBot


class UserAutoAssignment(commands.Cog):
    def __init__(self, bot: AdminBot):
        self.bot = bot

    @commands.slash_command(name="mentor", description="Assigns a user to be a mentor")
    @commands.has_permissions(manage_channels=True)
    async def mentor(self, ctx: discord.ApplicationContext,
                     user: discord.Option(discord.SlashCommandOptionType.user,
                                          description="The user to set as a mentor"),
                     category: discord.Option(choices=['0', '1'],  # future: don't hardcode
                                              description="The category"),
                     group_num: discord.Option(discord.SlashCommandOptionType.integer,
                                               description="The group number")):
        if group_num < 1:
            await ctx.respond("Does not make sense", ephemeral=True)
            return
        role_id = self.bot.sqlite_engine.cursor.execute("""
        SELECT linked_role_id FROM channel_store WHERE category_id = ? AND channel_number = ?""",
                                                        (category, group_num)).fetchone()
        if role_id is None:
            await ctx.respond("Database error, please contact developer. "
                              "(Note: This may occur if the group does not exist. "
                              "If it does not, please create the group)", ephemeral=True)
            return
        role_id = role_id[0]
        the_role = ctx.guild.get_role(role_id)
        if the_role is None:
            await ctx.respond("Role could not be fetched. "
                              "Please check bot permissions, "
                              "or check if the role has been deleted. "
                              "If the group does not exist, please create it", ephemeral=True)
            return
        usr: discord.Member = user
        await ctx.respond(f"Adding {str(user)} to {the_role.name}", ephemeral=True)
        await usr.add_roles(the_role, reason=f"codeexp_admin: User {ctx.author} set as mentor")

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: Exception):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond(str(error), ephemeral=True)
            return
        self.bot.logger.error(error)
        await ctx.respond("An error occurred, please contact developer", ephemeral=True)


def setup(bot: AdminBot):
    bot.add_cog(UserAutoAssignment(bot))
