import datetime
import traceback
import logging
import os
import sys
import time
from logging import handlers

import asyncio
import discord
from discord.ext import commands

from db import db

start = time.time()


class Error:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dir = os.path.dirname(__file__)
        self.taboo = os.environ["TABOO"] if "TABOO" in os.environ else ""  # used for hiding names from stack traces

        self.warning_icon = "https://i.imgur.com/4o1srPK.png"
        self.success_icon = "https://i.imgur.com/JSWM55t.png"
        self.denial_icon = "https://i.imgur.com/gOIGrSV.png"

    # Provides error messages for certain types of exception, and gives censored tracebacks for others (specifically,
    # CommandInvokeErrors, which wrap exceptions in the commands themselves)
    async def on_command_error(
            self,
            ctx: commands.Context,
            exception: Exception
    ):
        cog = ctx.cog
        if cog:
            attr = '_{0.__class__.__name__}__error'.format(cog)
            if hasattr(cog, attr):
                return

        icon = self.warning_icon
        message = ""

        # Handle known cases (poor OOP, look for ways to reimplement)
        if isinstance(exception, commands.CommandNotFound):
            message = "Command {} not found!".format(ctx.invoked_with)
        elif isinstance(exception, commands.CheckFailure):
            icon = self.denial_icon
        elif isinstance(exception, commands.MissingRequiredArgument):
            message = "Missing argument {}!".format(exception.param)
        elif isinstance(exception, commands.MissingPermissions):
            message = "You don't have the permissions to run this command!"
        elif isinstance(exception, commands.CommandOnCooldown):
            message = "This command is on cooldown! Please retry after {:.1f}s.".format(exception.retry_after)
            icon = "https://i.imgur.com/wF8KnYz.png"
        elif not isinstance(exception, commands.CommandInvokeError) and len(exception.args) != 0:
            message = exception.args[0]

        # If the exception isn't one of those, AND doesn't have an explanatory message, spew chunks
        else:
            try:
                exception = exception.original
            except AttributeError:
                pass

            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

            message = "Something's gone horribly wrong! Please contact @pandaxtc#0718 with details."
            await ctx.send(embed=discord.Embed().set_footer(
                text=message,
                icon_url=icon
            ).add_field(
                name="An exception occurred.",
                value="```{}```".format(
                    "".join(traceback.format_exception(
                        type(exception),
                        exception,
                        exception.__traceback__,
                        1
                    )).replace(
                        self.taboo,
                        "<filepath_censored>"
                    ))
            ))
            return

        # Send the error message, if it wasn't a CommandInvokeError
        await ctx.send(embed=discord.Embed().set_footer(
            text=message,
            icon_url=icon
        ))


if __name__ == "__main__":
    # Logging stuff
    log_dir = os.path.join(os.path.dirname(__file__), "./log/")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logfile_name = "ayano-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    root_logger = logging.getLogger("discord")
    root_logger.setLevel(logging.DEBUG)
    logger = logging.getLogger("discord.ayano")
    logger.setLevel(logging.DEBUG)

    file_handler = handlers.TimedRotatingFileHandler(
        filename=os.path.join(log_dir, logfile_name + ".log"),
        encoding="utf-8",
        when="D",
        interval=1,
        backupCount=16
    )
    std_handler = logging.StreamHandler(stream=sys.stdout)

    file_handler.setLevel(logging.DEBUG)
    std_handler.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] (%(name)s) %(message)s")
    file_handler.setFormatter(fmt)
    std_handler.setFormatter(fmt)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(std_handler)

    sys.path.append("..")

    # Base configuration
    dsc_token = os.environ["DISCORD_TOKEN"]

    bot_name = os.environ["BOT_NAME"]
    description = os.environ["DESCRIPTION"]
    playing = os.environ["PLAYING"]  # TODO: move into database
    extensions = os.environ["EXTENSIONS"].split(",")


    async def get_prefix(bot: discord.ext.commands.Bot, message: discord.Message):
        if message.guild is None:
            return "$"
        guild = await db.get_guild(message.guild.id)
        if guild is not None:
            return guild.prefix
        else:
            return "$"


    # Bot initialization
    bot = commands.Bot(command_prefix=get_prefix, description=description)

    # Benchmarking
    command_start_time = {}


    @bot.event
    async def on_ready():
        for guild in bot.guilds:
            await db.add_guild(db.Guild(id=guild.id))

        for autoreply in (await db.get_all_autoreplies(374158830831140866)):
            print(autoreply)

        logger.info(f" Logged in as <{bot.user.name}> <{bot.user.id}> ({time.time() - start} seconds)")
        logger.info(f"Running on discord.py v{discord.__version__}")
        await bot.change_presence(activity=discord.Activity(name=str(playing), type=0))


    @bot.event
    async def on_guild_join(guild: discord.Guild):
        await db.add_guild(db.Guild(id=guild.id))

    @bot.event
    async def on_guild_remove(guild: discord.Guild):
        await db.remove_guild

    @bot.before_invoke
    async def pre(ctx: commands.Context):
        logger.info(f"Command {ctx.command.name} triggered by user {ctx.author.name}<{ctx.author.id}>.")
        command_start_time[ctx.message.id] = time.clock()
        user = await db.get_user(ctx.author.id)
        if user is None:
            user = db.User(id=ctx.author.id)
            await db.add_user(user)
        await user.update(commands_executed=db.User.commands_executed + 1).apply()


    @bot.after_invoke
    async def post(ctx: commands.Context):
        try:
            elapsed = str(time.clock() - command_start_time.pop(ctx.message.id))
        except KeyError:
            elapsed = "N/A"
        logger.info(f"Command {ctx.command.name} triggered by user {ctx.author.name}<{ctx.author.id}> completed. "
                    f"Elapsed time: {elapsed}s")


    # Load error handler
    bot.add_cog(Error(bot))

    # Load cogs
    for e in extensions:
        bot.load_extension(e)

    bot.run(dsc_token)
