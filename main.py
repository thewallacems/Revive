import discord

import config
from bot import Revive
from logger import Logger

prefix = config.get('Bot', 'Prefix')
token = config.get('Bot', 'Token')

allowed_mentions = discord.AllowedMentions(everyone=False, roles=False, users=False)
bot = Revive(prefix, allowed_mentions=allowed_mentions)

bot.logger = Logger()
bot.logger.start()

bot.load_extension('cogs.library')
bot.load_extension('cogs.help')

try:
    bot.run(token)
except:
    bot.logger.exception('Unhandled while running bot')

bot.logger.join()
