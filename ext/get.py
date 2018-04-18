import asyncio
import datetime
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from zipfile import ZipFile

import aiohttp
import async_timeout
import discord
from discord.ext import commands

logger = logging.getLogger("discord.ayano." + __name__)


class Get():
    def __init__(self, bot):
        self.bot = bot
        self.dir = os.path.dirname(__file__)
        self.cache_dir = "cache/"
        self.safe_token = json.load(open("config.json"))["safe_token"]

    @commands.command()
    async def get(
            self,
            ctx: commands.Context,
            count: int
    ):
        """Sends the user links to the last  <x> attachments sent in the channel."""
        await ctx.trigger_typing()

        dl_dir = os.path.join(self.dir, self.cache_dir, datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f"))

        if 1 <= count <= 20:
            os.mkdir(dl_dir)
            counter = 0
            dupes = {}
            logger.info("Command invoked, searching...")
            start = time.time()

            async for message in ctx.history(limit=5000):
                #print(message)
                if message.author != ctx.message.author:
                    for attachment in message.attachments:
                        print(attachment)
                        if counter < count:
                            with async_timeout.timeout(10):
                                filename = attachment.filename
                                id = attachment.id
                                filepath = os.path.join(
                                    dl_dir,
                                    filename if filename not in dupes
                                    else (
                                            filename +
                                            os.path.splitext(filename)[0] +
                                            "(%s)" % dupes[filename] +
                                            os.path.splitext(filename)[1]
                                    )
                                )
                                logger.info("Now handling download of file %s <%s>", filename, id)

                                try:
                                    with open(filepath, 'wb') as f:
                                        await attachment.save(f)
                                    if filename in dupes:
                                        dupes[filename] += 1
                                    else:
                                        dupes[filename] = 1
                                except IOError as e:
                                    logger.warning("File error on file %s, id <%s>!", filename, id,
                                                   exc_info=True)

                            counter += 1
                        else:
                            break
                    if counter >= int(count):
                        break

            end = time.time()

            if counter != 0:
                logger.info("Download complete! Time elapsed: %f", end - start)

                logger.info("Zipping %d files...", counter)
                start = time.time()

                e = ThreadPoolExecutor()
                await asyncio.get_event_loop().run_in_executor(e, self.zip, dl_dir, dl_dir)

                end = time.time()
                logger.info("Zipping complete! Time elapsed: %f", end - start)

                logger.info("Uploading %s.zip", os.path.basename(dl_dir))
                start = time.time()

                with open(dl_dir + ".zip", "rb") as f:
                    url = "https://safe.moe/api/upload"
                    data = aiohttp.FormData(quote_fields=False)
                    data.add_field("files[]", f)
                    async with aiohttp.ClientSession() as session:
                        print("begin!")
                        async with session.post(url,
                                                headers={
                                                    "token":
                                                        self.safe_token
                                                }, data=data) as r:
                            print(await r.text())
                            result = await r.json()

                end = time.time()
                logger.info("Upload complete! Time elapsed: %f", end - start)
                await ctx.send(embed=discord.Embed().set_footer(
                    text="File upload complete ;)",
                    icon_url="https://i.imgur.com/JSWM55t.png"
                ))
                await ctx.author.send("Here's your file~: " + result["files"][0]["url"])

            else:
                logger.info("No images found. Time elapsed: %f", end - start)
                os.rmdir(dl_dir)
                raise commands.CommandError("No compatible images found :(")

        else:
            raise commands.CommandError("Usage: " + str(ctx.command) + " <number> where number ∈ (0,20]")

    def zip(self, dir, name):
        print(dir, name)
        zip = ZipFile(name + ".zip", "w")
        for root, dirs, files in os.walk(dir):
            for file in files:
                zip.write(os.path.join(root, file), os.path.basename(os.path.join(root, file)))
        zip.close()
        print("all done.")

    @commands.command()
    async def rmcache(self):
        os.rmdir(self.cache_dir)
        os.mkdir(self.cache_dir)


def setup(bot):
    bot.add_cog(Get(bot))
