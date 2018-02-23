from discord.ext import commands
from logging import handlers
import discord, random, sys, os, logging, datetime, json

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


@bot.event
async def on_ready():
    ayano_logger.info('Logged in as <' + bot.user.name + "> <" + bot.user.id + ">")


@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.command()
async def roll(dice: str):
    '''Rolls xdx'''
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices: str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))


@bot.command()
async def joined(member: discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined at {0.joined_at}'.format(member))


@bot.command()
async def exit():
    await bot.say("Shutting down...")
    sys.exit(0)


bot.load_extension("get")
dsc_token = json.load(open("token.json"))["dsc_token"]
bot.run(dsc_token)
