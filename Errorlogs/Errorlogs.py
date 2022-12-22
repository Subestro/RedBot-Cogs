import discord
import sys
from redbot.core import Config, commands

class Errorlogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=3393734172)
        default_global = {
            "error_channel_id": None
        }
        self.config.register_global(**default_global)

    @commands.command()
    async def error(self, ctx, channel: discord.TextChannel):
        await self.config.error_channel_id.set(channel.id)
        await ctx.send(f"Error channel set to {channel.mention}.")

    async def send_error(self, message: str):
        error_channel_id = await self.config.error_channel_id()
        if error_channel_id is not None:
            error_channel = self.bot.get_channel(error_channel_id)
            await error_channel.send(message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CheckFailure):
            return
        else:
            await self.send_error(f"Error occurred in {ctx.command.qualified_name}: {error}")
            await self.send_error(f"Redbot console error: {error}")

    def send_console_error(self, message: str):
        try:
            # Code that may cause an error
            1 / 0
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_message = f"Python console error: {e}\n"
            error_message += "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.send_error(error_message)

def setup(bot):
    bot.add_cog(Errorlogs(bot))
