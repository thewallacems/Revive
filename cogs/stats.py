import asyncio
import itertools
from datetime import datetime
from enum import Enum

import discord
from discord.ext import commands


class Statuses(Enum):
    UPTIME = 0
    WEBSITE = 1


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.start_time = datetime.utcnow()
        self.commands_used = 0
        self.unique_users = set()

        self.status_changer_task = self.bot.loop.create_task(self.status_changer())

    async def status_changer(self):
        await self.bot.wait_until_ready()

        statuses = itertools.cycle(Statuses)

        for status in statuses:
            if status == Statuses.UPTIME:
                # remove the seconds and milliseconds from each time
                start_time = datetime(self.start_time.year, self.start_time.month, self.start_time.day,
                                      self.start_time.hour, self.start_time.minute, 0, 0)

                current_time = datetime.utcnow()
                current_time = datetime(current_time.year, current_time.month, current_time.day,
                                        current_time.hour, current_time.minute, 0, 0)

                uptime = str(current_time - start_time)
                name = f'Uptime: {uptime}'
            elif status == Statuses.WEBSITE:
                name = 'https://revivalstory.net/home'
            else:
                raise NotImplementedError(f'{status} not implemented.')

            activity = discord.Activity(name=name, type=discord.ActivityType.playing)
            await self.bot.change_presence(activity=activity)
            await asyncio.sleep(2 * 60)

    def cog_unload(self):
        time_online = str(datetime.utcnow() - self.start_time)

        self.bot.logger.info(f'Bot uptime: {time_online}')
        self.bot.logger.info(f'Unique users: {len(self.unique_users):,}')
        self.bot.logger.info(f'Commands used: {self.commands_used:,}')

        self.status_changer_task.cancel()

    @commands.Cog.listener('on_command_completion')
    async def on_command_completion(self, ctx):
        self.commands_used += 1

        if ctx.author.id not in self.unique_users:
            self.unique_users.add(ctx.author.id)


def setup(bot):
    bot.add_cog(Stats(bot))
