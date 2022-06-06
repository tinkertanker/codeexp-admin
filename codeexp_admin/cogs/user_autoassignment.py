from typing import Optional, Union
# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands
# noinspection PyPackageRequirements
from discord.ext import bridge

from codeexp_admin import AdminBot, SqliteEngine


def check_usr_has_managed_role(user: discord.Member, role_prefix: str = "cat") -> Optional[str]:
    user_has_managed_role = [role.name for role in user.roles if role.name.lower().startswith(role_prefix)]
    return user_has_managed_role[0] if len(user_has_managed_role) > 0 else None


async def edit_msg(msg: Union[discord.Interaction, discord.Message],
                   new_content: str) -> Union[discord.Message, discord.InteractionMessage]:
    if isinstance(msg, discord.Interaction):
        return await msg.edit_original_message(content=new_content)
    return await msg.edit(content=new_content)


async def set_group(user: discord.Member, category: Union[str, int], group: int, *,
                    engine: SqliteEngine,
                    update_message: Optional[Union[discord.Interaction, discord.Message]] = None) -> bool:
    has_managed = check_usr_has_managed_role(user)
    # note: this force cast can lead to crashes
    category = int(category)
    if has_managed:
        if update_message:
            await edit_msg(update_message, f"You have a group! `{has_managed}`")
        return False
    role_id = engine.cursor.execute("""
                    SELECT linked_role_id FROM channel_store WHERE category_id = ? AND channel_number = ?""",
                                    (category, group)).fetchone()
    if role_id is None:
        if update_message:
            await edit_msg(update_message, "This role does not exist")
        return False
    the_role = user.guild.get_role(role_id[0])
    if the_role is None:
        if update_message:
            await edit_msg(update_message, "Cache error. Please contact the developers")
        return False

    if update_message:
        await edit_msg(update_message, f"You are now joining {the_role.name}")
    await user.add_roles(the_role, reason=f"codeexp_admin: User {user} joined cat {category} grp {group}")
    return True


class UserAutoAssignment(commands.Cog):
    def __init__(self, bot: AdminBot):
        self.bot = bot

    @commands.command(name="usermod")
    async def normie_join_group(self, ctx: discord.ApplicationContext, category: int, group_num: int):
        update_message = await ctx.send("Now processing your join request...")
        if category not in [0, 1]:
            await edit_msg(update_message, "Invalid category. Please choose: [0, 1]")
            return
        if group_num < 1:
            await edit_msg(update_message, "Invalid group. Please choose a number greater than 0")
            return
        await set_group(ctx.author, category, group_num,
                        engine=self.bot.sqlite_engine, update_message=update_message)

    @commands.slash_command(name="usermod", description="Joins a group")
    async def join_group(self, ctx: discord.ApplicationContext,
                         category: discord.Option(choices=['0', '1'],  # future: don't hardcode
                                                  description="The category"),
                         group_num: discord.Option(discord.SlashCommandOptionType.integer,
                                                   description="The group number")
                         ):
        if group_num < 1:
            await ctx.respond("Does not make sense", ephemeral=True)
            return
        usr: discord.Member = ctx.author
        update_message = await ctx.respond("Now processing", ephemeral=True)
        await set_group(usr, category, group_num, engine=self.bot.sqlite_engine,
                        update_message=update_message)

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
