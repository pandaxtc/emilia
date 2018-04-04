import datetime
import json
import logging
import os
import random
import sys
import time
import re
from logging import handlers

import discord
from discord.ext import commands

log_dir = os.path.join(os.path.dirname(__file__), "log/")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logfile_name = "ayano-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

root_logger = logging.getLogger('discord')
file_handler = handlers.RotatingFileHandler(filename=os.path.join(log_dir, logfile_name + ".log"),
                                            encoding='utf-8',
                                            mode='w+',
                                            maxBytes=131072,
                                            backupCount=16)
std_handler = logging.StreamHandler(stream=sys.stderr)

file_handler.setLevel(logging.DEBUG)
std_handler.setLevel(logging.INFO)

format = logging.Formatter("%(asctime)s [%(levelname)s] (%(name)s) %(message)s")
file_handler.setFormatter(format)
std_handler.setFormatter(format)

root_logger.addHandler(file_handler)
root_logger.addHandler(std_handler)
root_logger.setLevel(logging.DEBUG)

description = '''TOSHINO KYOUKO!'''
bot = commands.Bot(command_prefix='$', description=description)

ayano_logger = logging.getLogger('discord.ayano')

bot.warning_icon = "https://i.imgur.com/4o1srPK.png"
bot.success_icon = "https://i.imgur.com/JSWM55t.png"
bot.denial_icon = "https://i.imgur.com/gOIGrSV.png"

command_start_time = {}
itsjoke_on = False


@bot.event
async def on_ready():
    ayano_logger.info('Logged in as <' + bot.user.name + "> <" + str(bot.user.id) + ">")
    ayano_logger.info("Running on discord.py v" + discord.__version__)
    await bot.change_presence(activity=discord.Activity(name="Beta than ever!", type=0))


@bot.command()
async def itsjoke(ctx):
    global itsjoke_on
    if ctx.guild.id == 271512274647121921:
        c = commands.EmojiConverter()
        e = await c.convert(ctx, "<:itsjoke:427973801570074635>")
        async def ijl(message):
            if ctx.guild.id == 271512274647121921:
                if re.match("it'?s ?joke", message.content, re.IGNORECASE):
                    await message.add_reaction(e)

        if not itsjoke_on:
            itsjoke_on = True
            bot.add_listener(ijl, "on_message")
            await ctx.send("its joke!")
        elif itsjoke_on:
            itsjoke_on = False
            bot.remove_listener(ijl)
            await ctx.send("its not joke...")
    else:
        await ctx.send("its joke!")


# It's alive!
@bot.before_invoke
async def pre(ctx: commands.Context):
    ayano_logger.info("Command {command} triggered by user {username}<{uid}>.".format(
        command=ctx.command.name,
        username=ctx.author.display_name,
        uid=ctx.author.id
    ))
    command_start_time[ctx.message.id] = time.clock()


@bot.after_invoke
async def post(ctx: commands.Context):
    try:
        elapsed = str(time.clock() - command_start_time.pop(ctx.message.id))
    except KeyError:
        elapsed = "N/A"
    ayano_logger.info(
        "Command {command} triggered by user {username}<{uid}> completed. Elapsed time: {time}s".format(
            command=ctx.command.name,
            username=ctx.author.display_name,
            uid=ctx.author.id,
            time=elapsed
        ))


@bot.command()
async def roll(ctx, dice: str):
    '''Rolls xdx'''
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        raise commands.CommandError("Format must be NdN!")

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(embed=discord.Embed().set_footer(
        text=result,
        icon_url="https://i.imgur.com/jvHOTmJ.png"
    ))


@bot.command(description="For when you wanna settle the score some other way")
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(embed=discord.Embed().set_footer(
        text="I choose " + random.choice(choices) + "!",
        icon_url="https://i.imgur.com/gkgrjRa.png"
    ))


@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(embed=discord.Embed().set_footer(
        text="{0.name} joined at {0.joined_at}".format(member),
        icon_url="https://i.imgur.com/xAYyvuw.png"
    ))


@bot.command()
async def exit(ctx):
    await ctx.send("Shutting down...")
    bot.logout()


bot.load_extension("cogs.get")
bot.load_extension("cogs.birthday")
bot.load_extension("cogs.autoreact")
bot.load_extension("cogs.error")
dsc_token = json.load(open("config.json"))["dsc_token"]
bot.run(dsc_token)
