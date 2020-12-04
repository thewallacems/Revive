import discord
from discord.ext import commands


class Library(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_ready')
    async def on_ready(self):
        await self.bot.db.connect()
        self.bot.logger.info('Connected to database.')

    @commands.command(
        help='Looks up by name in the RevivalStory Library',
        description='Looks up by name in the RevivalStory Library',
    )
    async def lookup(self, ctx, *, name: str):
        item = await self.bot.db.search(name)
        if item is None:
            return

        embed = discord.Embed.from_dict(item.to_embed_dict())
        embed.set_thumbnail(url=item.get_image_url())
        return await ctx.send(embed=embed)

    @commands.command(
        help='Searches all items in the given category (equips, items, monsters) with the given condition',
        description='Searches all items in the given category (equips, items, monsters) with the given condition\n'
                    'Conditions are formatted `<field>` `<operator>` `<value>`\n'
                    'Operators include any combination of `<`, `>`, and `=`\n'
                    'Value is an integer.'
    )
    async def search(self, ctx, category: str, *, condition: str):
        values = await self.bot.db.where(category, condition)
        if not values:
            return

        try:
            return await ctx.send(f'Returned value(s): {values}')
        except discord.HTTPException:
            return await ctx.send('Please narrow your search.')


def setup(bot):
    bot.add_cog(Library(bot))
