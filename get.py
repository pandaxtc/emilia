from discord.ext import commands
import requests, os, aiohttp, datetime, logging, threading
from concurrent.futures.thread import ThreadPoolExecutor
from zipfile import ZipFile

logger = logging.getLogger("discord.ayano." + __name__)


class Get():
    def __init__(self, bot):
        self.bot = bot
        self.dir = os.path.dirname(__file__)

    def dlWorker(self, attachment, dupes, dl_dir, layer):
        thread_name = threading.current_thread().name
        try:
            filename = attachment["filename"]
            id = attachment["id"]
            logger.info("(%s) Now handling download of file %s <%s>", thread_name, filename, id)
            try:
                r = requests.get(attachment["url"])
            except Exception:
                logger.warning("(%s) Attachment %s <%s> download error: ", thread_name, filename, id, exc_info=True)
            else:
                try:
                    if filename in dupes:
                        dupes[filename] += 1
                    else:
                        dupes[filename] = 1
                    with open(os.path.join(self.dir,
                                           "cache/", dl_dir,
                                           filename if filename not in dupes
                                           else (os.path.splitext(filename)[0] +
                                                 "(%s)" % dupes[filename] + os.path.splitext(filename)[1])), "xb") as f:

                        f.write(r.content)
                        logger.info("(%s) Attachment %s <%s> saved!", thread_name, filename, id)
                except FileExistsError as e:
                    if filename in dupes and dupes["filename"] != 1:
                        dupes[filename] -= 1
                    else:
                        dupes.pop(filename, None)
                    if (layer < 16):
                        logger.warning("(%s) File collision detected, retrying download of file %s <%s> (attempt %d)",
                                       thread_name, filename, id, layer + 1)
                        self.dlWorker(attachment, dupes, dl_dir, layer)
                    else:
                        logger.warning("(%s) File collision detected, too many attempts. Abandoning file %s <%s>",
                                       thread_name, filename, id)
                except IOError as e:
                    logger.warning("(%s) File error on file %s, id <%s>!", filename, id, exc_info=True)
        except:
            logger.warning("(%s) Whoops, something went wrong.", thread_name, exc_info=True)

    @commands.command(pass_context=True)
    async def get(self, ctx, count: str):
        """Sends the user links to the last <x> attachments sent in the channel."""
        dl_dir = os.path.join(self.dir, "cache/", datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f"))
        os.mkdir(dl_dir)
        if count.isdigit() and 1 <= int(count) <= 20:
            counter = 0
            dupes = {}
            logger.info("Command invoked, spawning threads...")
            with ThreadPoolExecutor(thread_name_prefix="dlWorker") as executor: # blocking, TODO: fix
                async for message in self.bot.logs_from(ctx.message.channel, limit=500):
                    for attachment in message.attachments:
                        if counter < int(count):
                            executor.submit(self.dlWorker, attachment, dupes, dl_dir, 0)
                            counter += 1
                        else:
                            break
                    if counter >= int(count):
                        break
            logger.info("Complete!")
            if counter != 0:
                await self.bot.say(
                    ctx.message.author.mention + ", downloaded " + str(counter) + " images :kissing_heart:")
            else:
                await self.bot.say("No compatible images found :cry:")
                os.rmdir(dl_dir)
        else:
            await self.bot.say("Usage: " + str(ctx.command) + " <number> where number ∈ (0,20]")

        zip = ZipFile(dl_dir + ".zip", "w")
        for root, dirs, files in os.walk(dl_dir):
            for file in files:
                zip.write(os.path.join(root, file), os.path.basename(os.path.join(root, file)))
        zip.close()

        # TODO: upload the files to a hosting service. see: https://github.com/aio-libs/aiohttp/issues/903


def setup(bot):
    bot.add_cog(Get(bot))
