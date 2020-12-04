from discord.ext import commands


class HelpCommand(commands.DefaultHelpCommand):
    async def send_error_message(self, error):
        #  don't send any error message to stop spam
        return


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        #  save the original help command if this cog is unloaded
        self._original_help_command = bot.help_command

        #  move the help command to this cog
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        #  if this cog is unloaded, keep the default help command
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Help(bot))
