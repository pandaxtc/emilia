import logging
import os

import discord
from discord.ext import commands

logger = logging.getLogger("discord.emilia." + __name__)


class Dev:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dir = os.path.dirname(__file__)

    @commands.command(alises=["embed, emb"])
    async def embed_footer(
            self,
            ctx: commands.Context,
            footer_icon="https://i.imgur.com/JSWM55t.png",
            footer_text="Test text."
    ):
        """Send a test dialog. Usage: embed_footer <icon_url> <text>"""
        embed = discord.Embed()
        embed.set_footer(
            text=footer_text,
            icon_url=footer_icon
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["raise", "exc"])
    async def raise_exc(
            self,
            ctx: commands.Context
    ):
        """Raise an exception."""
        raise Exception("This is a test exception.")

    @commands.command()
    @commands.is_owner()
    async def eval(
            self,
            ctx: commands.Context,
            *,
            statement: str
    ):
        """Dumb eval, locked to bot owner only. Do not use!"""
        eval(statement)


def setup(bot):
    bot.add_cog(Dev(bot))
