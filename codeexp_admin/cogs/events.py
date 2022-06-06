# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands

from codeexp_admin import AdminBot, SqliteEngine
import random
import string


def create_captcha(engine: SqliteEngine, discord_id: int) -> str:
    """
    Creates a captcha for a user
    :param engine: The SqliteEngine
    :param discord_id: The Discord ID of the user
    :return: The captcha
    """
    captcha_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    engine.cursor.execute("""
    INSERT INTO members (discord_id, captcha, captcha_passed) VALUES (?, ?, 0)""",
                          (discord_id, captcha_str))
    return captcha_str


def verify_captcha(engine: SqliteEngine, discord_id: int, captcha_text: str) -> bool:
    """
    Retrieves captcha text for a user

    Args:
        engine: The SqliteEngine
        discord_id: The Discord ID of the user
        captcha_text: The captcha text

    Returns:
        True if the captcha is correct, False otherwise

    """
    engine.cursor.execute("""
    SELECT captcha FROM members WHERE discord_id = ?""", (discord_id,))
    captcha_str = engine.cursor.fetchone()
    if captcha_str is None:
        return False
    if captcha_str[0] == captcha_text:
        engine.cursor.execute("""
        UPDATE members SET captcha_passed = 1 WHERE discord_id = ?""", (discord_id,))
        return True
    return False


class EventHandlers(commands.Cog):

    def __init__(self, bot: AdminBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return

        if message.content.startswith("/usermod"):
            args = message.content.split(" ")
            if len(args) < 3:
                await message.channel.send("Usage: /usermod <cat> <grp>")
                return

            if not args[1].isdigit():
                await message.channel.send("Please do not include strings. Your cat and grp ids are numeric!")
                return
            await message.channel.send(f"{message.author.mention}, you need to be patient and wait for "
                                       f"the autocomplete to pop up before using this command.")
            return

            # if message.content.startswith("!captcha"):
            #     args = message.content.split(" ")
            #     if len(args) != 2:
            #         await message.channel.send("Usage: !captcha [captcha]")
            #         return
            #     captcha_text = args[1]
            #     our_server = self.bot.get_guild(self.bot.cfg.guild)
            #     user_in_our_server = our_server.get_member(message.author.id)
            #     if user_in_our_server:
            #         msg = await message.channel.send("Verifying captcha...")
            #         cap_verified = verify_captcha(self.bot.sqlite_engine, user_in_our_server.id, captcha_text)
            #         if cap_verified:
            #             await msg.edit(content="Captcha verified! You are now approved to join the server")
            #             await user_in_our_server.add_roles(our_server.
            #                                                get_role(self.bot.cfg.mentor_role))
            #             return
            #         await msg.edit(content="Could not verify your captcha. Either your captcha is incorrect, "
            #                                "or you are already verified. If you believe this is an error, "
            #                                "please contact us")
            #         return
            #     await message.channel.send("You are not in our server. Please join the server and try again.")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id != self.bot.debug_guilds[0]:
            return
        dm = await member.create_dm()
        # captcha_text = create_captcha(self.bot.sqlite_engine, member.id)
        # await dm.send(f"Welcome to the CODE_EXP 2022 server\n"
        #               f"1. To get started, please react with a :white_check_mark: in the #rules channel "
        #               f"to see the other channels."
        #               f"2. Head to #botspam and type in `/usermod [category: YourCategory] "
        #               f"[group_num: YourGroupNumber]`. "
        #               f"Refer to the invite email for `YourCategory` and `YourGroupNumber`."
        #               f"3. Make sure you see the channels called `#cat-X-grp-Y-txt` and `cat-X-grp-Y-vc`. "
        #               f"These are your text and voice channels, private to you, your team, and your mentors. "
        #               f"4. If you have any questions or issues, please ask in #discord-help.")
        # await dm.send(f"Please reply to me with the following : `!captcha {captcha_text}`")
        # if member.name.lower().startswith("dsta mentor"):
        #     await member.add_roles(member.guild.get_role(self.bot.cfg.mentor_role))
        #     await dm.send(f"Welcome, {member.mention}! You have been assigned to the mentor role.")


def setup(bot: AdminBot):
    bot.add_cog(EventHandlers(bot))
