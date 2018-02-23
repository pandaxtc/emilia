from discord.ext import commands
from zipfile import ZipFile
import os, datetime, logging, async_timeout, aiohttp, time, json

logger = logging.getLogger("discord.ayano." + __name__)


class Get():
    def __init__(self, bot):
        self.bot = bot
        self.dir = os.path.dirname(__file__)
        self.cache_dir = "cache/"
        self.safe_token = json.load(open("token.json"))["safe_token"]

    @commands.command(pass_context=True)
    async def get(self, ctx, count: str):
        """Sends the user links to the last  <x> attachments sent in the channel."""
        await self.bot.send_typing(ctx.message.channel)
        dl_dir = os.path.join(self.dir, self.cache_dir, datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f"))
        if count.isdigit() and 1 <= int(count) <= 20:
            os.mkdir(dl_dir)
            counter = 0
            dupes = {}
            logger.info("Command invoked, searching...")
            start = time.time()

            async with aiohttp.ClientSession() as session:
                async for message in self.bot.logs_from(ctx.message.channel, limit=500):
                    if message.author !=ctx.message.author:
                        for attachment in message.attachments:
                            if counter < int(count):
                                with async_timeout.timeout(10):
                                    async with session.get(attachment['url']) as response:
                                        filename = attachment["filename"]
                                        id = attachment["id"]
                                        filepath = os.path.join(dl_dir,
                                                                filename if filename not in dupes
                                                                else (filename +
                                                                      os.path.splitext(filename)[0] +
                                                                      "(%s)" % dupes[filename] +
                                                                      os.path.splitext(filename)[1]))
                                        logger.info("Now handling download of file %s <%s>", filename, id)

                                        try:
                                            with open(filepath, 'wb') as f:
                                                while True:
                                                    chunk = await response.content.read(1024)
                                                    if not chunk:
                                                        break
                                                    f.write(chunk)
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

                # blocking, TODO: fix
                zip = ZipFile(dl_dir + ".zip", "w")
                for root, dirs, files in os.walk(dl_dir):
                    for file in files:
                        zip.write(os.path.join(root, file), os.path.basename(os.path.join(root, file)))
                zip.close()

                end = time.time()
                logger.info("Zipping complete! Time elapsed: %f", end - start)

                logger.info("Uploading %s.zip", os.path.basename(dl_dir))
                start = time.time()

                with open(dl_dir + ".zip", "rb") as f:
                    url = "https://safe.moe/api/upload"
                    data = aiohttp.FormData(quote_fields=False)
                    data.add_field("files[]", f)
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url,
                                                headers={
                                                    "token":
                                                        self.safe_token
                                                }, data=data) as r:
                            result = await r.json()

                end = time.time()
                logger.info("Upload complete! Time elapsed: %f", end - start)
                await self.bot.say(ctx.message.author.mention + ", fetched " + str(counter) + " images :kissing_heart:")
                await self.bot.send_message(ctx.message.author, "Here's your file~: " + result["files"][0]["url"])

            else:
                logger.info("No images found. Time elapsed: %f", end - start)
                await self.bot.say("No compatible images found :cry:")
                os.rmdir(dl_dir)

        else:
            await self.bot.say("Usage: " + str(ctx.command) + " <number> where number ∈ (0,20]")

    @commands.command()
    async def rmcache(self):
        os.rmdir(self.cache_dir)
        os.mkdir(self.cache_dir)


def setup(bot):
    bot.add_cog(Get(bot))
