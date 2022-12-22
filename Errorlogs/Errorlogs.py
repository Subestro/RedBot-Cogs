import discord
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

def setup(bot):
    bot.add_cog(Errorlogs(bot))
