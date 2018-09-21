import logging
import os

import discord
from discord.ext import commands

logger = logging.getLogger("discord.emilia." + __name__)


class Util:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dir = os.path.dirname(__file__)

    @commands.command(aliases=["ch_info"])
    async def channel_info(
            self,
            ctx: commands.Context,
            channel: discord.TextChannel = None
    ):
        await ctx.trigger_typing()

        if channel is None:
            channel = ctx.channel

        name = channel.name
        topic = channel.topic
        created_at = channel.created_at
        id = channel.id
        category = str(channel.category) if channel.category is not None else ""
        count_pins = len(await channel.pins())
        count_webhooks = len(await channel.webhooks())

        out = discord.Embed(
            description=topic
        )
        if ctx.guild.icon_url != "":
            out.set_thumbnail(url=ctx.guild.icon_url)
        out.set_author(
            name=f"#{name} Info",
            icon_url="https://a.safe.moe/8JnbFv9.PNG"
        )
        out.add_field(
            name="Created at",
            value=created_at,
            inline=False
        )
        out.add_field(
            name="ID",
            value=id,
            inline=True
        )
        out.add_field(
            name="Category",
            value=category
        )
        out.add_field(
            name="Pins",
            value=str(count_pins),
            inline=True
        )
        out.add_field(
            name="Webhooks",
            value=str(count_webhooks),
            inline=True
        )
        out.set_footer(
            text=f"{ctx.guild.name}",
        )

        await ctx.send(embed=out)

    @commands.command(aliases=["ch_activity"])
    async def channel_activity(
            self,
            ctx: commands.Context,
            channel: discord.TextChannel = None,
            user: discord.User = None,
            limit: int = 5000,
    ):
        await ctx.trigger_typing()

        if channel is None:
            channel = ctx.channel

        count_total_messages = 0
        count_user_messages = {}

        if user is None:
            async for message in channel.history(limit=limit):
                count_total_messages += 1
                if message.author in count_user_messages:
                    count_user_messages[message.author] += 1
                else:
                    count_user_messages[message.author] = 1
        else:
            count_user_messages[user] = 0
            async for message in channel.history(limit=limit):
                count_total_messages += 1
                if message.author == user:
                    count_user_messages[user] += 1

        most_active_users = sorted(count_user_messages, key=count_user_messages.get, reverse=True)[:5]

        user_string = f"for {user.display_name}" if user is not None else ""
        cap_string = "(capped)" if count_total_messages == limit else ""

        out = discord.Embed()
        if ctx.guild.icon_url != "":
            out.set_thumbnail(url=ctx.guild.icon_url)
        out.set_author(
            name=f"#{channel.name} Channel Activity {user_string}",
            icon_url="https://a.safe.moe/MTc2Hp3.png"
        )
        for user in most_active_users:
            count = count_user_messages[user]
            out.add_field(
                name=user.display_name,
                value=f"{count} messages | {count/count_total_messages*100:.2f}%"
            )
        out.set_footer(
            text=f"Total messages checked: {count_total_messages} {cap_string}",
        )

        await ctx.send(embed=out)


def setup(bot):
    bot.add_cog(Util(bot))
