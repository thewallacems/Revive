import json
import os
import os.path
import sys
import time
from collections import Counter

import discord
from discord.ext import commands

from database.database import Database


def _save_blacklist(blacklist):
    if blacklist:
        with open('blacklist.json', 'w') as file:
            json.dump(blacklist, file, indent=4)
    else:
        if os.path.exists('blacklist.json'):
            os.remove('blacklist.json')


def _load_blacklist():
    if not os.path.exists('blacklist.json'):
        return dict()
    else:
        with open('blacklist.json', 'r') as file:
            return json.load(file)


class Revive(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

        self.db = Database()

        self.rate_limiter = commands.CooldownMapping.from_cooldown(1.0, 2.0, commands.BucketType.user)
        self.rate_counter = Counter()
        self.blacklist = _load_blacklist()

    async def on_ready(self):
        self.logger.info(f'{self.user} logged in')

    async def on_message(self, message):
        if message.author.bot or str(message.author.id) in self.blacklist:
            return

        return await self.process_commands(message)

    async def process_commands(self, message):
        ctx = await self.get_context(message)

        if ctx.command is None:
            return

        if await self._check_rate_limit(message):
            return await message.add_reaction('🛑')

        if message.author.id in self.rate_counter:
            self.rate_counter.pop(message.author.id)

        await self.invoke(ctx)

    async def on_command_error(self, ctx, error):
        ignored = (commands.CommandNotFound, commands.CheckFailure, commands.MissingRequiredArgument,
                   discord.Forbidden,)
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return

        message = f'An error occurred while processing command:\n\t{ctx.author}: {ctx.message.content}'
        exc_info = (type(error), error, error.__traceback__,)
        self.logger.exception(message, exc_info)

    async def on_error(self, event_method, *args, **kwargs):
        message = f'An error occurred in the bot in {event_method}'
        self.logger.exception(message, sys.exc_info())

    async def close(self):
        await self.db.disconnect()
        self.logger.info('Database disconnected')

        await super().close()
        self.logger.info('Bot logged off')
        self.logger.join()

        _save_blacklist(self.blacklist)

    async def _check_rate_limit(self, message):
        author = message.author
        if author.id == self.owner_id:
            return False

        bucket = self.rate_limiter.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            self.rate_counter[author.id] += 1
            if self.rate_counter[author.id] >= 5:
                self.blacklist[str(message.author.id)] = time.time()
                self.logger.info(f'{author} blocked for spam.')
                try:
                    await author.send('You have been blocked from using this bot temporarily due to spam.')
                except discord.HTTPException:
                    await message.channel.send(f'You have been blocked from using this bot temporarily due to spam, '
                                               f'{author.mention}.')

        return retry_after
