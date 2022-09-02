# Leah
# commands.py
# Written by aquova et al., 2022
# https://github.com/StardewValleyDiscord/leah

import strings
import discord
from discord.ext import commands
from importlib import reload
from utils import requires_admin


class Commands(commands.Cog):
    posted = set()

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="sync")
    @commands.check(requires_admin)
    async def sync(self, message: discord.Message) -> None:
        await self.bot.sync_guild(message.guild)
        await message.reply(content=strings.get("commands_response_sync"))

    @commands.command(name="strings")
    @commands.check(requires_admin)
    async def reload_strings(self, message: discord.Message) -> None:
        reload(strings)
        self.bot.reload_strings()
        await message.reply(content=strings.get("commands_response_strings"))

    @commands.command(name="commands")
    @commands.check(requires_admin)
    async def reload_commands(self, message: discord.Message) -> None:
        await self.bot.reload_extension(name="commands")
        await message.reply(content=strings.get("commands_response_commands"))

async def setup(bot: commands.Bot) -> None:
    cog: Commands = Commands(bot)
    await bot.add_cog(cog)
    reload(strings)
