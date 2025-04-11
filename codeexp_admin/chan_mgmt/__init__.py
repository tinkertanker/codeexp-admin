from typing import Union, Optional
from collections import namedtuple
import enum

# noinspection PyPackageRequirements
import discord

from codeexp_admin import SqliteEngine

prefix = "cat"


def get_last_grp_num(engine: SqliteEngine, category: int) -> int:
    cur = engine.cursor.execute(
        """
    SELECT channel_number FROM channel_store WHERE category_id = ? ORDER BY channel_number DESC LIMIT 1
    """,
        (category,),
    )
    result = cur.fetchone()
    if result is None:
        return 0
    else:
        return result[0]


def get_managed_channels(
    guild: discord.Guild, category: int
) -> list[Union[discord.TextChannel, discord.VoiceChannel]]:
    # do not ever change this code or you will cry
    managed_channels = list(
        filter(
            lambda channel: channel.name.lower().startswith(
                f"{prefix.lower()}-{category}"
            ),
            guild.channels,
        )
    )
    return managed_channels


def get_managed_roles(
    guild: discord.Guild, category: int
) -> Optional[list[discord.Role]]:
    managed_roles = list(
        filter(lambda role: role.name.startswith(f"{prefix}-{category}"), guild.roles)
    )
    return managed_roles if len(managed_roles) > 0 else None


async def create_managed_channel(
    guild: discord.Guild,
    category: int,
    channel_number: int,
    *,
    engine: SqliteEngine,
    update_message: Optional[discord.Interaction],
):
    pass


async def create_managed_channels(
    guild: discord.Guild,
    category: int,
    num_channels: int = 1,
    *,
    engine: SqliteEngine,
    update_message: Optional[discord.Interaction],
):
    last_group_num = get_last_grp_num(engine, category)
    for i in range(num_channels):
        if update_message:
            await update_message.edit_original_message(
                content=f"Creating group #{last_group_num + i + 1}"
            )
        role = await guild.create_role(
            name=f"{prefix}-{category}-grp-{last_group_num + i + 1}"
        )
        category_name = f"{prefix}-{category}-grp-{last_group_num + i + 1}"
        cat = await guild.create_category(category_name)
        await cat.set_permissions(role, read_messages=True, send_messages=True, connect=True, speak=True,reason="Created by codeexp_admin")
        await cat.set_permissions(guild.default_role, read_messages=False, connect=False, reason="Created by codeexp_admin")
        for gtype in ["txt", "vc"]:
            group_name = f"{prefix}-{category}-grp-{last_group_num + i + 1}-{gtype}"
            if gtype == "txt":
                chan = await guild.create_text_channel(group_name, category=cat)
                engine.cursor.execute(
                    """
                INSERT INTO channel_store (discord_channel_id, discord_channel_name, channel_type, category_id,
                 channel_number, linked_role_id)  VALUES (?, ?, ?, ?, ?, ?) 
                """,
                    (
                        chan.id,
                        group_name,
                        "text",
                        category,
                        last_group_num + i + 1,
                        role.id,
                    ),
                )
                engine.connection.commit()

            elif gtype == "vc":
                chan = await guild.create_voice_channel(group_name, category=cat)
                engine.cursor.execute(
                    """
                                INSERT INTO channel_store (discord_channel_id, discord_channel_name, channel_type, category_id,
                 channel_number, linked_role_id) VALUES (?, ?, ?, ?, ?, ?) 
                                """,
                    (
                        chan.id,
                        group_name,
                        "voice",
                        category,
                        last_group_num + i + 1,
                        role.id,
                    ),
                )
                engine.connection.commit()
    if update_message:
        await update_message.edit_original_message(
            content=f"Created {num_channels} channels"
        )


async def delete_managed_channels(
    guild: discord.Guild,
    category: int,
    *,
    engine: SqliteEngine,
    update_message: Optional[discord.Interaction],
):
    managed_chans = get_managed_channels(guild, category)
    managed_roles = get_managed_roles(guild, category)
    for channel in managed_chans:
        if update_message:
            await update_message.edit_original_message(
                content=f"Deleting channel {channel.name}"
            )
        await channel.delete()
        engine.cursor.execute(
            """
        DELETE FROM channel_store WHERE discord_channel_id = ?
        """,
            [channel.id],
        )
        engine.connection.commit()

    for role in managed_roles:
        if update_message:
            await update_message.edit_original_message(
                content=f"Deleting role {role.name}"
            )
        await role.delete()
