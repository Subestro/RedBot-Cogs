import discord
from discord.ext import commands
from redbot.core import Config

class rTraktCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Replace with your own identifier
        default_global = {
            "trakt_client_id": "",
            "trakt_client_secret": "",
            "trakt_refresh_token": "",
            "discord_channel_id": 0  # Default channel ID
        }
        self.config.register_global(**default_global)

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.command()
    @commands.is_owner()
    async def setchannel(self, ctx, channel: discord.TextChannel):
        await self.config.discord_channel_id.set(channel.id)
        await ctx.send(f"Channel set to: {channel.mention}")

    @commands.command()
    @commands.is_owner()
    async def settraktcredentials(self, ctx, client_id, client_secret):
        await self.config.trakt_client_id.set(client_id)
        await self.config.trakt_client_secret.set(client_secret)
        await ctx.send("Trakt credentials set successfully.")

    @commands.command()
    @commands.is_owner()
    async def settraktchannel(self, ctx, channel: discord.TextChannel):
        await self.config.discord_channel_id.set(channel.id)
        await ctx.send(f"Trakt channel set to: {channel.mention}")

def setup(bot):
    bot.add_cog(rTraktCog(bot))
