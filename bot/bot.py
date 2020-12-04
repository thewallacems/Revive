from discord.ext import commands

from database.database import Database


class Revive(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        self.db = Database()

    async def on_ready(self):
        self.logger.info(f'{self.user} logged in')

    async def close(self):
        await self.db.disconnect()
        self.logger.info('Database disconnected')

        await super().close()
        self.logger.info('Bot logged off')

    async def on_command_error(self, ctx, error):
        message = f'An error occurred while processing command:\n\t{ctx.author}: {ctx.message.contents}'
        self.logger.exception(message)

    async def on_error(self, event_method, *args, **kwargs):
        message = 'An error occurred in the bot!'
        self.logger.exception(message)
