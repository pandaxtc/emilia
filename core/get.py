import asyncio
import datetime
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from zipfile import ZipFile

import aiohttp
import async_timeout
import discord
from discord.ext import commands

logger = logging.getLogger("discord.emilia." + __name__)


class Get:
    def __init__(self, bot):
        self.bot = bot
        self._upload_url = "https://safe.moe/api/upload"
        self._safe_token = os.environ["SAFE_TOKEN"]
        if not os.path.exists("core/cache/"):
            os.mkdir("core/cache/")

    @commands.command()
    async def get(
            self,
            ctx: commands.Context,
            count: int
    ):
        """Sends the user links to the last <x> attachments sent in the channel."""
        await ctx.trigger_typing()

        if not 1 <= count <= 20:
            raise commands.CommandError(f"Usage: {str(ctx.command)} <number> where number ∈ (0,20]")

        dl_dir = os.path.join(
            os.path.dirname(__file__),
            "cache/",
            datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f")
        )
        os.mkdir(dl_dir)

        counter = 0
        dupes = {}
        dl_start = time.time()  # Benchmarking

        async for message in ctx.history(limit=5000):
            if counter >= count:
                break
            if message.author != ctx.message.author:
                for attachment in message.attachments:
                    if counter >= count:
                        break
                    with async_timeout.timeout(3):
                        filename = attachment.filename
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
                        logger.info(f"Now handling download of file {filename} <{attachment.id}>")

                        try:
                            with open(filepath, 'wb') as f:
                                await attachment.save(f)
                            if filename in dupes:
                                dupes[filename] += 1
                            else:
                                dupes[filename] = 1
                        except IOError:
                            logger.warning(f"File error on file {filename}, id <{attachment.id}>!", exc_info=True)

                    counter += 1

        dl_end = time.time()  # Benchmarking
        logger.info(f"Download complete! Time elapsed: {dl_end - dl_start}")

        if counter == 0:
            logger.info(f"No images found. Time elapsed: {dl_end - dl_start}")
            os.rmdir(dl_dir)
            raise commands.CommandError("No compatible images found!")

        logger.info(f"Zipping {counter} files...")
        zip_start = time.time()  # Benchmarking

        e = ThreadPoolExecutor()
        await asyncio.get_event_loop().run_in_executor(e, self.zip_dir, dl_dir, dl_dir)

        zip_end = time.time()  # Benchmarking
        logger.info(f"Zipping complete! Time elapsed: {zip_end - zip_start}")

        logger.info(f"Uploading {os.path.basename(dl_dir)}.zip")
        upload_start = time.time()  # Benchmarking

        with open(dl_dir + ".zip", "rb") as f:
            data = aiohttp.FormData(quote_fields=False)
            data.add_field("files[]", f)
            async with aiohttp.ClientSession() as session:
                async with session.post(self._upload_url,
                                        headers={
                                            "token":
                                                self._safe_token
                                        }, data=data) as r:
                    result = await r.json()
        zip_url = result["files"][0]["url"]

        upload_end = time.time()  # Benchmarking
        logger.info(f"Upload complete! Time elapsed: {upload_end - upload_start}")
        await ctx.send(embed=discord.Embed().set_footer(
            text="File upload complete ;)",
            icon_url="https://i.imgur.com/JSWM55t.png"
        ))
        await ctx.author.send(f"Here's your file~: {zip_url}")

    def zip_dir(self, dir, name):
        zip = ZipFile(name + ".zip", "w")
        for root, dirs, files in os.walk(dir):
            for file in files:
                zip.write(os.path.join(root, file), os.path.basename(os.path.join(root, file)))
        zip.close()

    @commands.command()
    async def rmcache(self):
        os.rmdir("cache/")
        os.mkdir("cache/")


def setup(bot):
    bot.add_cog(Get(bot))
