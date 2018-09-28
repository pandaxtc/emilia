import os
import sys
import traceback

import discord
from discord.ext import commands

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
            attr = f"_{cog.__class__.__name__}__error"
            if hasattr(cog, attr):
                return

        icon = self.warning_icon
        message = ""

        # Handle known cases (poor OOP, look for ways to reimplement)
        # if isinstance(exception, commands.CommandNotFound):
        #    message = "Command {} not found!".format(ctx.invoked_with)
        if isinstance(exception, commands.CheckFailure):
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
                    ))[:960]
            ))
            return

        # Send the error message, if it wasn't a CommandInvokeError
        await ctx.send(embed=discord.Embed().set_footer(
            text=message,
            icon_url=icon
        ))
