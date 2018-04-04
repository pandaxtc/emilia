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
        with open("autoreact.json", "r") as f:
            self.ar_dict = json.load(f)

        async def autoreact(message):
            if message.author != self.bot.user:
                if str(message.guild.id) in self.ar_dict:
                    for rgx in self.ar_dict[str(message.guild.id)]:
                        try:
                            async with async_timeout.timeout(2):
                                if re.match(rgx, message.content):
                                    await message.channel.send(self.ar_dict[str(message.guild.id)][rgx])
                        except asyncio.TimeoutError:
                            pass

        bot.add_listener(autoreact, 'on_message')

    @commands.group(aliases=["ar"])
    async def autoreact(
            self,
            ctx: commands.Context,
    ):
        """Configure autoreact for this server."""
        await ctx.trigger_typing()

        if ctx.invoked_subcommand is None:
            if ctx.subcommand_passed is None:
                raise commands.CommandError("Please specify a subcommand!")

    @autoreact.group()
    async def add(
            self,
            ctx: commands.Context,
            rgx: str,
            emote: str
    ):
        await ctx.trigger_typing()

        # Check if emote is a unicode emoji
        valid_emoji = emote in emoji.UNICODE_EMOJI

        # If emote wasn't a unicode emoji, check for custom emoji
        if not valid_emoji:
            try:
                converter = commands.EmojiConverter()
                emoji_str = await converter.convert(ctx, emote)
            except commands.BadArgument as e:
                raise e  # If was not custom emoji, raise exception and leave command
        else:  # If emote *was* valid emoji, deemojize
            emoji_str = emoji.demojize(emote)

        self.ar_dict[str(ctx.guild.id)][rgx] = str(emoji_str)

        await asyncio.get_event_loop().run_in_executor(None, self.write_to_json, self.ar_dict, "autoreact.json")

        await ctx.send(embed=discord.Embed().set_footer(
            text="Added autoreact {}!".format(rgx),
            icon_url="https://i.imgur.com/JSWM55t.png"
        ))

    @autoreact.group()
    async def rm(
            self,
            ctx: commands.Context,
            rgx: str
    ):
        await ctx.trigger_typing()
        try:
            self.ar_dict[str(ctx.guild.id)].pop(rgx)
        except KeyError:
            raise commands.CommandError("Autoreact " + rgx + " not found.")

        await asyncio.get_event_loop().run_in_executor(None, self.write_to_json, self.ar_dict, "autoreact.json")

        await ctx.send(embed=discord.Embed().set_footer(
            text="Removed autoreact {}!".format(rgx),
            icon_url="https://i.imgur.com/JSWM55t.png"
        ))

    def write_to_json(
            self,
            data: dict,
            file: str
    ):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)


def setup(bot):
    bot.add_cog(Autoreact(bot))
