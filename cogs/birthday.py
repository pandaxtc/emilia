import asyncio
import discord
import datetime
import time
import json
import logging
import os
from collections import deque
from discord.ext import commands

logger = logging.getLogger("discord.ayano." + __name__)


class Birthday:
    def __init__(self, bot):
        self.bot = bot
        self.dir = os.path.dirname(__file__)
        self.cache_dir = "cache/"
        with open("bday.json", "r") as f:
            self.bdays = json.load(f)
        with open("token.json", "r") as f:
            j = json.load(f)
            self.bd_guilds = j["bd_guilds"]
        self.bd_sleepers = {}

    async def on_ready(self):
        for guild in self.bd_guilds:
            asyncio.ensure_future(self.bd_chk(int(guild), int(self.bd_guilds[guild])))

    @commands.group(aliases=["bd", "bday"])
    async def birthday(
            self,
            ctx: commands.Context
    ):
        if ctx.invoked_subcommand is None:
            if ctx.subcommand_passed is None:
                raise commands.CommandError("Please specify a subcommand!")

            converter = commands.MemberConverter()
            member = await converter.convert(
                ctx,
                ctx.subcommand_passed if ctx.subcommand_passed is not None else ""
            )

            try:
                bd = self.bdays[str(member.id)]
                await ctx.send(embed=discord.Embed().set_footer(
                    text="{name}'s birthday is on {date}!".format(
                        name=member.display_name,
                        date=bd[:2] + "/" + bd[2:]
                    ),
                    icon_url="https://i.imgur.com/3KdYtqn.png"
                ))
            except KeyError:
                raise commands.CommandError("Member {name} has no registered birthday!".format(
                    name=member.display_name
                ))

    @birthday.command()
    async def add(
            self,
            ctx: commands.Context,
            member: discord.Member,
            month: str,
            day: int
    ):
        """Add a birthday. Usage: <user> <month> <day>"""
        try:  # datetime object's purpose is to act as a date parser
            bday = datetime.datetime.strptime(month + " " + str(day) + " 2000", "%B %d %Y")
        except ValueError:
            raise commands.CommandError("Incorrect format! Usage: <month> <day>")
        self.bdays[str(member.id)] = bday.strftime("%m%d")

        await asyncio.get_event_loop().run_in_executor(None, self.write_to_json, self.bdays, "bday.json")

        await ctx.send(embed=discord.Embed().set_footer(
            text="Added member {}!".format(member),
            icon_url="https://i.imgur.com/JSWM55t.png"
        ))

        await ctx.invoke(self.refresh)

    @birthday.command(aliases=["rm"])
    async def remove(
            self,
            ctx: commands.Context,
            member: discord.Member
    ):
        try:
            self.bdays.pop(member.id, None)
        except KeyError:
            raise commands.CommandError("Member " + str(member) + " not found.")

        print(self.bdays)

        await asyncio.get_event_loop().run_in_executor(None, self.write_to_json, self.bdays, "bday.json")

        await ctx.send(embed=discord.Embed().set_footer(
            text="Removed member {}!".format(member),
            icon_url="https://i.imgur.com/JSWM55t.png"
        ))

        await ctx.invoke(self.refresh)

    @birthday.command()
    async def refresh(
            self,
            ctx: commands.Context
    ):
        logger.info("Refreshed birthday roles for guild %s.", ctx.guild.id)
        logger.info("Current birthdays: " + str(self.bdays))
        self.bd_sleepers[ctx.guild.id].cancel()

        await ctx.send(embed=discord.Embed().set_footer(
            text="Refreshed all birthdays!",
            icon_url="https://i.imgur.com/JSWM55t.png"
        ))

    def write_to_json(
            self,
            data: dict,
            file: str
    ):
        with open(file, "w") as f:
            json.dump(data, f)

    async def bd_chk(self, guildid: int, roleid: int):
        while True:
            logger.info("Checking birthdays...")

            if len(self.bdays) > 0:
                now = datetime.datetime.today()
                this_time_tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                guild = self.bot.get_guild(guildid)
                members = guild.members
                bd_role = discord.utils.get(guild.roles, id=roleid)

                logger.info("Today is %d/%d.", now.month, now.day)

                for m in members:
                    if m.id != guild.owner.id:
                        id = m.id
                        try:
                            month = int(self.bdays[str(id)][:2])
                            day = int(self.bdays[str(id)][2:])
                            logger.info("Registered birthday %d/%d found for user %s.", month, day, str(m))
                            if month == now.month and day == now.day:
                                logger.info("Hit, updating role.")
                                await m.add_roles(bd_role)
                            elif bd_role in m.roles:
                                await m.remove_roles(bd_role)
                        except KeyError:
                            if bd_role in m.roles:
                                await m.remove_roles(bd_role)

                time_to_tomorrow = (datetime.datetime.combine(
                    this_time_tomorrow,
                    datetime.datetime.min.time()
                ) - now).total_seconds()

                coro = asyncio.sleep(time_to_tomorrow)
                self.bd_sleepers[guildid] = asyncio.ensure_future(coro)
                try:
                    await self.bd_sleepers[guildid]
                except asyncio.CancelledError:
                    pass
            else:
                logger.info("No birthdays registered. Waiting...")

                coro = asyncio.sleep(60)
                self.bd_sleepers[guildid] = asyncio.ensure_future(coro)
                try:
                    await self.bd_sleepers[guildid]
                except asyncio.CancelledError:
                    pass


def setup(bot):
    bot.add_cog(Birthday(bot))
