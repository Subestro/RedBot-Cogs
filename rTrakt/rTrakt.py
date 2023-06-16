import discord
from redbot.core import commands, Config
import trakt

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Use a unique identifier for your cog
        default_guild = {
            "channel_id": None,
            "client_id": None,
            "client_secret": None
        }
        self.config.register_guild(**default_guild)

    @commands.group()
    async def rtraktset(self, ctx):
        """Commands to set rTrakt settings"""
        pass

    @rtraktset.command()
    async def channel(self, ctx, channel: discord.TextChannel):
        """Set the channel where the results should be sent"""
        await self.config.guild(ctx.guild).channel_id.set(channel.id)
        await ctx.send(f"Results will be sent to {channel.mention}")

    @rtraktset.command()
    async def credentials(self, ctx, client_id, client_secret):
        """Set the Trakt API credentials"""
        await self.config.guild(ctx.guild).client_id.set(client_id)
        await self.config.guild(ctx.guild).client_secret.set(client_secret)
        await ctx.send("Trakt API credentials set!")

    @commands.command()
    async def checkcredentials(self, ctx):
        """Check if the Trakt API credentials are working"""
        client_id = await self.config.guild(ctx.guild).client_id()
        client_secret = await self.config.guild(ctx.guild).client_secret()
        if client_id is None or client_secret is None:
            await ctx.send("API credentials not set. Use `[p]rtraktset credentials` to set the credentials.")
            return

        try:
            trakt.init(client_id=client_id, client_secret=client_secret)
            trakt_user = trakt.users.User("me")
            watched = trakt_user.watched(type="episodes", limit=1)
            await ctx.send("API credentials are working!")
        except trakt.errors.APIException as e:
            await ctx.send(f"API credentials are not valid. Error: {str(e)}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.bot:
            return

        channel_id = await self.config.guild(after.guild).channel_id()
        if channel_id is None:
            return

        client_id = await self.config.guild(after.guild).client_id()
        client_secret = await self.config.guild(after.guild).client_secret()
        if client_id is None or client_secret is None:
            return

        trakt.init(client_id=client_id, client_secret=client_secret)
        trakt_user = trakt.users.User("me")
        watched = trakt_user.watched(type="episodes", limit=1)

        if watched:
            title = watched[0].show.title
            channel = self.bot.get_channel(channel_id)
            await channel.send(f"{after.display_name} is currently watching: {title}")

def setup(bot):
    cog = rTrakt(bot)
    bot.add_cog(cog)
