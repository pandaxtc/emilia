import datetime
import logging
import os
import sys
import time
import traceback
from logging import handlers

import discord
from discord.ext import commands

from db import db
from error import Error

start = time.time()

if __name__ == "__main__":
    # Logging stuff
    log_dir = os.path.join(os.path.dirname(__file__), "./log/")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logfile_name = "emilia-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    root_logger = logging.getLogger("discord")
    root_logger.setLevel(logging.DEBUG)
    logger = logging.getLogger("discord.emilia")
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
        logger.info(f" Logged in as <{bot.user.name}> <{bot.user.id}> ({time.time() - start} seconds)")
        logger.info(f"Running on discord.py v{discord.__version__}")
        await bot.change_presence(activity=discord.Activity(name=str(playing), type=0))


    @bot.event
    async def on_guild_join(guild: discord.Guild):
        await db.add_guild(db.Guild(id=guild.id))


    @bot.event
    async def on_guild_remove(guild: discord.Guild):
        db_guild = await db.get_guild(guild.id)
        await db.remove_guild(db_guild)


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


    bot.add_cog(Error(bot))

    # Load cogs
    for e in extensions:
        bot.load_extension(e)

    bot.run(dsc_token)
