from datetime import datetime

from discord.ext import commands


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.start_time = datetime.utcnow()
        self.commands_used = 0
        self.unique_users = set()

    def cog_unload(self):
        time_online = str(datetime.utcnow() - self.start_time)

        self.bot.logger.info(f'Bot uptime: {time_online}')
        self.bot.logger.info(f'Unique users: {len(self.unique_users):,}')
        self.bot.logger.info(f'Commands used: {self.commands_used:,}')

    @commands.Cog.listener('on_command_completion')
    async def on_command_completion(self, ctx):
        self.commands_used += 1

        if ctx.author.id not in self.unique_users:
            self.unique_users.add(ctx.author.id)


def setup(bot):
    bot.add_cog(Stats(bot))
