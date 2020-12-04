import time

from discord.ext import commands


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def block(self, ctx, id: str):
        if id not in self.bot.blacklist:
            self.bot.blacklist[id] = time.time()
            return await ctx.message.add_reaction('👍')

    @commands.command(hidden=True)
    async def unblock(self, ctx, id: str):
        if id in self.bot.blacklist:
            self.bot.blacklist.pop(id)
            return await ctx.message.add_reaction('👍')

    def cog_check(self, ctx):
        try:
            block_id = int(ctx.message.content.split(' ')[1])
            return block_id != self.bot.owner_id and ctx.author.id == self.bot.owner_id
        except:
            return False


def setup(bot):
    bot.add_cog(Mod(bot))
