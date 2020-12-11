from datetime import datetime

import aiohttp
from discord.ext import commands, tasks

from tracking import onlinecount, rankings

_POLLING_RATE = 1 / 2

_FMT_TIME = '%m/%d/%Y %H:%M:%S'


class Tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracker.start()

    @tasks.loop(minutes=60 * _POLLING_RATE)
    async def tracker(self):
        await self.bot.wait_until_ready()

        async with aiohttp.ClientSession() as session:
            online_count = await onlinecount.get_online_count(session)
            characters = await rankings.get_rankings(session)

            time = datetime.utcnow().strftime(_FMT_TIME).split(' ')
            date = time[0]
            time = time[1]

            async with self.bot.pool.acquire() as connection:
                if online_count is not None:
                    query = 'INSERT INTO "OnlineCount" VALUES($1, $2, $3);'
                    await connection.execute(query, date, time, online_count)

                if characters is not None:
                    query = 'INSERT INTO "Characters" VALUES($1, $2, $3, $4, $5);'
                    await connection.executemany(query, characters)

    @tracker.error
    async def tracker_eh(self, error):
        message = 'Error during tracking'
        exc_info = (type(error), error, error.__traceback__,)
        self.bot.logger.exception(message, exc_info)


def setup(bot):
    bot.add_cog(Tracker(bot))
