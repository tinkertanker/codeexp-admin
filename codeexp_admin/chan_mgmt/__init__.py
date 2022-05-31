from typing import Union, Optional
from collections import namedtuple
import enum

# noinspection PyPackageRequirements
import discord

prefix = "tkam"


def get_last_grp_num(guild: discord.Guild, category: int) -> int:
    # this code is truly awful
    managed = get_managed_channels(guild, category)
    if len(managed) == 0:
        return 0
    managed.sort(key=lambda channel: int(channel.name.split("-")[-1]))
    highest = int(managed[-1].name.split("-")[-1])
    return highest


def get_managed_channels(guild: discord.Guild, category: int) -> list[Union[discord.TextChannel, discord.VoiceChannel]]:
    # do not ever change this code or you will cry
    managed_channels = list(
        filter(
            lambda channel: channel.name.lower().startswith(f"{prefix.lower()}-{category}"),
            guild.channels
        )
    )
    return managed_channels


async def create_managed_channels(guild: discord.Guild, category: int, num_channels: int = 1,
                                  *,
                                  update_message: Optional[discord.Interaction]):
    last_group_num = get_last_grp_num(guild, category)
    for i in range(num_channels):
        if update_message:
            await update_message.edit_original_message(content=f"Creating {last_group_num + i + 1}")
        for gtype in ["txtgrp", "vcgrp"]:
            group_name = f"{prefix}-{category}-{gtype}-{last_group_num + i + 1}"
            if gtype == "txtgrp":
                await guild.create_text_channel(group_name)
            elif gtype == "vcgrp":
                await guild.create_voice_channel(group_name)


async def delete_managed_channels(guild: discord.Guild, category: int,
                                  *,
                                  update_message: Optional[discord.Interaction]):
    managed_chans = get_managed_channels(guild, category)
    for channel in managed_chans:
        if update_message:
            await update_message.edit_original_message(content=f"Deleting {channel.name}")
        await channel.delete()
