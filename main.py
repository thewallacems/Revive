import discord

import config
from bot import Revive
from logger import Logger

prefix = config.get('Bot', 'Prefix')
token = config.get('Bot', 'Token')

allowed_mentions = discord.AllowedMentions.none()
bot = Revive(prefix, allowed_mentions=allowed_mentions)

bot.logger = Logger()
bot.logger.start()

bot.load_extension('cogs.library')
bot.load_extension('cogs.help')

try:
    bot.run(token)
except:
    if bot.logger.is_alive():
        bot.logger.fatal('Unhandled exception while running bot')
    else:
        import traceback
        traceback.print_exc()
