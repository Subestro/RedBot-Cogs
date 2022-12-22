import discord
from redbot.core import commands

class Errorlogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_channel = None

    @commands.command()
    async def set_error_channel(self, ctx, channel_id: int):
        channel = discord.utils.get(ctx.guild.channels, id=channel_id)
        if channel is None:
            await ctx.send("Invalid channel ID.")
        else:
            self.error_channel = channel
            await ctx.send(f"Error channel set to {channel.mention}.")

    async def send_error(self, message: str):
        if self.error_channel is not None:
            await self.error_channel.send(message)

def setup(bot):
    bot.add_cog(Errorlogs(bot))
