from typing import Optional, Union

# noinspection PyPackageRequirements
import discord

# noinspection PyPackageRequirements
from discord.ext import commands

from discord.utils import get

# noinspection PyPackageRequirements
from discord.ext import bridge
from discord import SlashCommandOptionType as ScOt

from codeexp_admin import AdminBot, SqliteEngine


def check_usr_has_managed_role(
    user: discord.Member, role_prefix: str = "cat"
) -> Optional[str]:
    """
    This function checks if a user has a role managed by the bot.
    Used to prevent people from joining more than 1 group.

    Args:
        user: The discord.Member instance of the user
        role_prefix: The role prefix of the user

    Returns:
        The role name if the user has a role managed by the bot, None otherwise
    """
    user_has_managed_role = [
        role.name for role in user.roles if role.name.lower().startswith(role_prefix)
    ]
    return user_has_managed_role[0] if len(user_has_managed_role) > 0 else None


async def edit_msg(
    msg: Union[discord.Interaction, discord.Message], new_content: str
) -> Union[discord.Message, discord.InteractionMessage]:
    """
    A flexible edit message function that allows you to edit both
     Interactions and regular Messages.
    Note that the edit is immediately processed,
    and you are simply seeing the result of the edit.

    Args:
        msg: The message
        new_content: The new content to place in the message.

    Returns:
        The edited message.
    """
    if isinstance(msg, discord.Interaction):
        return await msg.edit_original_message(content=new_content)
    return await msg.edit(content=new_content)


async def set_group(
    user: discord.Member,
    category: Union[str, int],
    group: int,
    *,
    bot: AdminBot,
    engine: SqliteEngine,
    update_message: Optional[Union[discord.Interaction, discord.Message]] = None,
) -> bool:
    """
    Modifies the group of a user

    Args:
        user: The discord.Member to modify
        category: The category they would like to join
        group: The group they would like to join
        engine: The SqliteEngine. Pass in the one that is currently in use.
        update_message: Optionally, the message to edit to show the user
                        that processing is taking place.
                        Also where errors are sent
        bot: The AdminBot instance

    Returns:
        True or False depending on whether the operation was able to complete
    """
    has_managed = check_usr_has_managed_role(user)
    # note: this force cast MIGHT lead to crashes. use sentry to monitor this.
    category = int(category)
    if has_managed:
        mentor_role = user.guild.get_role(bot.cfg.mentor_role)
        if mentor_role.id not in [role.id for role in user.roles]:
            # user cannot join multiple groups if they are not a mentor
            if update_message:
                await edit_msg(update_message, f"You have a group! `{has_managed}`")
            return False
    role_id = engine.cursor.execute(
        """SELECT linked_role_id FROM channel_store WHERE 
        category_id = ? AND channel_number = ?""",
        (category, group),
    ).fetchone()
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
    await user.add_roles(
        the_role,
        reason=f"codeexp_admin: User {user} " f"joined cat {category} grp {group}",
    )
    return True


class UserAutoAssignment(commands.Cog):
    def __init__(self, bot: AdminBot):
        self.bot = bot

    @commands.command(name="joingroup")
    async def normie_join_group(
        self, ctx: discord.ApplicationContext, category: int, group_num: int
    ):
        """
        This command is used to join a group for a user.

        Args:
            ctx: The discord.ApplicationContext instance
            category: The category to join
            group_num: The group to join

        Returns:
            None

        """
        update_message = await ctx.send("Now processing your join request...")
        if category not in [0, 1]:
            await edit_msg(update_message, "Invalid category. Please choose: [1, 2]")
            return
        if group_num < 1:
            await edit_msg(
                update_message,
                "Invalid group. Please choose a " "number greater than 0",
            )
            return
        await set_group(
            ctx.author,
            category,
            group_num,
            bot=self.bot,
            engine=self.bot.sqlite_engine,
            update_message=update_message,
        )
        # TODO: Don't hardcode
        # sets user to also have the 'participant' role
        await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name="participant"))

    @commands.slash_command(name="joingroup", description="Joins a group")
    async def join_group(
        self,
        ctx: discord.ApplicationContext,
        category: discord.Option(
            choices=["1", "2"],
            # future: don't hardcode
            description="The category",
        ),
        group_num: discord.Option(ScOt.integer, description="The group number"),
    ):
        if group_num < 1:
            await ctx.respond("Does not make sense", ephemeral=True)
            return
        usr: discord.Member = ctx.author
        update_message = await ctx.respond("Now processing", ephemeral=True)
        await set_group(
            usr,
            category,
            group_num,
            bot=self.bot,
            engine=self.bot.sqlite_engine,
            update_message=update_message,
        )
        # TODO: Don't hardcode
        # sets user to also have the 'joined' role
        await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name="verified"))


    @commands.slash_command(name="dstamentor", description="Assign yourself the mentor role - requires a secret password")
    async def dstamentor(
        self,
        ctx: discord.ApplicationContext,
        password
    ):
        if password == self.bot.cfg.mentor_role_password:
            usr: discord.Member = ctx.author
            update_message = await ctx.respond("Success!", ephemeral=True)
            # TODO: Don't hardcode
            # sets user to have the 'mentor' role
            await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name="dsta-mentor"))
        else:
            await ctx.respond("Invalid password!", ephemeral=True)


    @commands.slash_command(name="mentor", description="Assigns a user to be a mentor of a specific group, requires the dsta-mentor role")
    @commands.has_permissions(manage_channels=True)

    async def mentor(
        self,
        ctx: discord.ApplicationContext,
        # user: discord.Option(
        #     discord.SlashCommandOptionType.user,
        #     description="The user to set as a mentor",
        # ),
        category: discord.Option(
            choices=["1", "2"],
            # future: don't hardcode
            description="The category",
        ),
        group_num: discord.Option(
            discord.SlashCommandOptionType.integer, description="The group number"
        ),
    ):
        if group_num < 1:
            await ctx.respond("Does not make sense", ephemeral=True)
            return
        role_id = self.bot.sqlite_engine.cursor.execute(
            """
        SELECT linked_role_id FROM channel_store WHERE category_id = ? 
        AND channel_number = ?""",
            (category, group_num),
        ).fetchone()
        if role_id is None:
            await ctx.respond(
                "Database error, please contact developer. "
                "(Note: This may occur if the group does not exist. "
                "If it does not, please create the group)",
                ephemeral=True,
            )
            return
        
        role = discord.utils.get(ctx.guild.roles, name="dsta-mentor")
        if role not in ctx.author.roles:
            await ctx.respond(f"Only mentors can run this command!", ephemeral=True)
            return

        role_id = role_id[0]
        the_role = ctx.guild.get_role(role_id)
        if the_role is None:
            await ctx.respond(
                "Role could not be fetched. "
                "Please check bot permissions, "
                "or check if the role has been deleted. "
                "If the group does not exist, please create it",
                ephemeral=True,
            )
            return
        usr: discord.Member = ctx.author
        await ctx.respond(f"Adding {str(ctx.author)} to {the_role.name}", ephemeral=True)
        await usr.add_roles(
            the_role, reason=f"codeexp_admin: User {ctx.author} " f"set as mentor"
        )

    @commands.Cog.listener()
    async def on_application_command_error(
        self, ctx: discord.ApplicationContext, error: Exception
    ):
        if isinstance(error, commands.MissingPermissions):
            self.bot.logger.error("Error because of missing perms")
            await ctx.respond(str(error), ephemeral=True)
            return
        self.bot.logger.error(error)
        await ctx.respond("An error occurred, please contact developer", ephemeral=True)


def setup(bot: AdminBot):
    bot.add_cog(UserAutoAssignment(bot))
