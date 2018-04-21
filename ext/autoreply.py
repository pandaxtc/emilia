import asyncio
import json
import async_timeout
import logging
import os
import discord
import re

import emoji
from discord.ext import commands

logger = logging.getLogger("discord.ayano." + __name__)


class Autoreact():
    def __init__(self, bot):
        self.bot = bot
        self.dir = os.path.dirname(__file__)

        with open("autoreply.json", "r", encoding='utf-8') as f:
            self.ar_dict = json.load(f)

        async def ar_listener(message):
            if message.author != self.bot.user:
                if str(message.guild.id) in self.ar_dict:
                    logger.info(f"Message \"{message.content}\"<{message.id}> in autoreply guild. Checking matches:")
                    for rgx in self.ar_dict[str(message.guild.id)]:
                        logger.info(f"Checking {rgx}...")
                        try:
                            async with async_timeout.timeout(2):
                                if re.match(rgx, message.content, re.IGNORECASE):
                                    logger.info(f"Autoreply hit on message <{message.id}> on regex {rgx}.")
                                    await message.channel.send(self.ar_dict[str(message.guild.id)][rgx])
                        except asyncio.TimeoutError:
                            logger.info(f"Timeout on message <{message.id}> on regex {rgx}.")

        bot.add_listener(ar_listener, 'on_message')

    async def on_ready(self):
        logger.info(f"Registered autoreplies: {self.ar_dict}")

    @commands.group(aliases=["ar"])
    async def autoreply(
            self,
            ctx: commands.Context,
    ):
        """Configure autoreact for this server."""
        await ctx.trigger_typing()

        if ctx.invoked_subcommand is None:
            if ctx.subcommand_passed is None:
                raise commands.CommandError("Please specify a subcommand!")

    @autoreply.group(alises=["ls"])
    async def list(
            self,
            ctx: commands.Context
    ):
        """List autoreacts for this server."""
        await ctx.trigger_typing()


    @autoreply.group()
    async def add(
            self,
            ctx: commands.Context,
            rgx: str,
            reply: str
    ):
        await ctx.trigger_typing()

        self.ar_dict[str(ctx.guild.id)][rgx] = reply

        await asyncio.get_event_loop().run_in_executor(None, self.write_to_json, self.ar_dict, "autoreply.json")

        await ctx.send(embed=discord.Embed().set_footer(
            text=f"Added autoreply {rgx}!",
            icon_url="https://i.imgur.com/JSWM55t.png"
        ))

    @autoreply.group(aliases=["rm"])
    async def remove(
            self,
            ctx: commands.Context,
            rgx: str
    ):
        await ctx.trigger_typing()
        try:
            self.ar_dict[str(ctx.guild.id)].pop(rgx)
        except KeyError:
            raise commands.CommandError("Autoreact " + rgx + " not found.")

        await asyncio.get_event_loop().run_in_executor(None, self.write_to_json, self.ar_dict, "autoreply.json")

        await ctx.send(embed=discord.Embed().set_footer(
            text=f"Removed autoreply {rgx}!",
            icon_url="https://i.imgur.com/JSWM55t.png"
        ))

    def write_to_json(
            self,
            data: dict,
            file: str
    ):
        with open(file, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


def setup(bot):
    bot.add_cog(Autoreact(bot))