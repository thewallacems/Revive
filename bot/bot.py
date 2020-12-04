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
        self.logger.join()

    async def on_command_error(self, ctx, error):
        ignored = (commands.CommandNotFound, )

        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return

        message = f'An error occurred while processing command:\n\t{ctx.author}: {ctx.message.content}'
        exc_info = (type(error), error, error.__traceback__, )
        self.logger.exception(message, exc_info)

    async def on_error(self, event_method, *args, **kwargs):
        message = f'An error occurred in the bot in {event_method}'
        self.logger.exception(message)
