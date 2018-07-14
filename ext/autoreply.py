import asyncio
import json
import async_timeout
import logging
import os
import discord
import re

from discord.ext import commands
from concurrent.futures import ProcessPoolExecutor, TimeoutError

from db import db

logger = logging.getLogger("discord.ayano." + __name__)


# Processes communicate through serializable objects only; re.match does not return one
def match_wrapper(*args):
    if re.match(*args):
        return True
    else:
        return False


class Autoreply:
    def __init__(self, bot):
        self.bot = bot
        self.dir = os.path.dirname(__file__)

        async def ar_listener(message):
            if message.author != self.bot.user:
                guild = await db.get_guild(message.guild.id)
                if guild.autoreply_on:
                    logger.debug(f"Message \"{message.content}\"<{message.id}> in autoreply guild. Checking matches:")
                    for autoreply in (await db.get_all_autoreplies(message.guild.id)):
                        rgx = autoreply.regex
                        pool = ProcessPoolExecutor(1)
                        result = False
                        try:
                            async with async_timeout.timeout(0.5):
                                result = await bot.loop.run_in_executor(pool, match_wrapper, rgx, message.content,
                                                                        re.IGNORECASE)
                        except TimeoutError:
                            for pid in pool._processes:
                                pool._processes[pid].terminate()
                            logger.debug(f"Timeout on message <{message.id}> on regex {rgx}.")
                        if result:
                            logger.debug(f"Autoreply hit on message <{message.id}> on regex {rgx}.")
                            await message.channel.send(autoreply.reply)
                        else:
                            logger.debug(f"No hit on message <{message.id}> on regex {rgx}.")

        bot.add_listener(ar_listener, 'on_message')

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

    @autoreply.command
    async def toggle(
            self,
            ctx: commands.Context
    ):
        """Toggles autoreact for this server."""
        await ctx.trigger_typing()

        guild = await db.get_guild(ctx.guild.id)
        await guild.update(autoreact_on=not guild.autoreply_on_on).apply()

        state = "on" if not guild.autoreply_on else "off"
        await ctx.send(embed=discord.Embed().set_footer(
            text=f"Turned {state} autoreplies!",
            icon_url="https://i.imgur.com/JSWM55t.png"
        ))


    @autoreply.command(alises=["ls"])
    async def list(
            self,
            ctx: commands.Context
    ):
        """Lists autoreacts for this server."""
        await ctx.trigger_typing()

        autoreplies = await db.get_all_autoreplies(ctx.guild.id)

        out = discord.Embed()
        if ctx.guild.icon_url != "":
            out.set_thumbnail(url=ctx.guild.icon_url)
        out.set_author(
            name="Configured Autoreplies",
            icon_url="https://i.imgur.com/ziSrf9Y.png"
        )
        for autoreply in autoreplies:
            out.add_field(
                name=autoreply.regex,
                value=autoreply.reply
            )
        await ctx.send(embed=out)

    @autoreply.command()
    async def add(
            self,
            ctx: commands.Context,
            rgx: str,
            reply: str
    ):
        await ctx.trigger_typing()

        max_count_autoreplies = int(os.environ["MAX_AUTOREPLIES"])
        count_autoreplies = len(await db.get_all_autoreplies(ctx.guild.id))

        if count_autoreplies > max_count_autoreplies:
            raise commands.CommandError(f"You cannot have more than {max_count_autoreplies} autoreplies!")

        autoreply = db.Autoreply(guild_id=ctx.guild.id, regex=rgx, reply=reply)
        await db.add_autoreply(autoreply)

        await ctx.send(embed=discord.Embed().set_footer(
            text=f"Added autoreply!",
            icon_url="https://i.imgur.com/JSWM55t.png"
        ))

    @autoreply.command(aliases=["rm"])
    async def remove(
            self,
            ctx: commands.Context,
            rgx: str
    ):
        await ctx.trigger_typing()

        autoreply = await db.get_autoreply(ctx.guild.id, rgx)
        if autoreply is None:
            raise commands.CommandError("Autoreply not found!")

        await db.delete_autoreply(ctx.guild.id, rgx)

        await ctx.send(embed=discord.Embed().set_footer(
            text=f"Removed autoreply!",
            icon_url="https://i.imgur.com/JSWM55t.png"
        ))


def setup(bot):
    bot.add_cog(Autoreply(bot))
