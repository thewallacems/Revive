import asyncio
import itertools
from datetime import datetime

import discord
from discord.ext import commands


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.start_time = datetime.utcnow()
        self.commands_used = 0
        self.unique_users = set()

        self.status_changer_task = self.bot.loop.create_task(self.status_changer())

    async def status_changer(self):
        await self.bot.wait_until_ready()

        statuses = itertools.cycle([0, 1])

        for status in statuses:
            if status == 0:
                activity = discord.Activity(name='https://revivalstory.net/home', type=discord.ActivityType.playing)
            else:
                current_time = datetime.utcnow()
                uptime = str(current_time - self.start_time).split('.')[0]
                activity = discord.Activity(name=f'Uptime: {uptime}', type=discord.ActivityType.playing)

            await self.bot.change_presence(activity=activity)
            await asyncio.sleep(10 * 60)

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
