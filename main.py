import sys

import discord

import config
from bot import Revive
from logger import Logger

prefix = config.get('Bot', 'Prefix')
token = config.get('Bot', 'Token')
owner_id = config.getint('Bot', 'OwnerID')

allowed_mentions = discord.AllowedMentions.none()

intents = discord.Intents.none()
intents.messages = True
intents.guild_reactions = True
intents.guilds = True

bot = Revive(prefix, allowed_mentions=allowed_mentions, intents=intents, owner_id=owner_id)

bot.logger = Logger()
bot.logger.start()

bot.load_extension('cogs.help')
bot.load_extension('cogs.library')
bot.load_extension('cogs.mod')
bot.load_extension('cogs.stats')

try:
    bot.run(token)
except:
    if bot.logger.is_alive():
        exc_info = sys.exc_info()
        bot.logger.fatal('Unhandled exception while running bot', exc_info)
    else:
        import traceback

        traceback.print_exc()
