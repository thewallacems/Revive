import discord
from discord.ext import commands

from database import models, database


class Library(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None

    @commands.command(
        help='Looks up by name in the RevivalStory Library',
        description='Looks up by name in the RevivalStory Library',
    )
    async def lookup(self, ctx, *, name: str):
        item = await self.db.search(name)
        if isinstance(item, list):
            return await ctx.send(f'Did you mean... `{"`, `".join(item)}`?')
        elif isinstance(item, (models.Monster, models.Equip, models.Item)):
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
        values = await self.db.where(category, condition)
        if not values:
            return

        try:
            return await ctx.send(f'Returned value(s): `{"`, `".join(values)}`')
        except discord.HTTPException:
            return await ctx.send('Please narrow your search.')

    async def cog_before_invoke(self, ctx):
        if self.db is None:
            self.db = database.Database(self.bot.pool)


def setup(bot):
    bot.add_cog(Library(bot))
