import discord
from redbot.core import commands, Config
import requests
import trakt
import asyncio
from trakt.errors import NotFoundException, TraktException

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567000)  # Change identifier to a unique integer
        default_global = {
            "trakt_client_id": None,
            "trakt_client_secret": None
        }
        self.config.register_global(**default_global)
        self.channel_id = None
        self.last_watched = None
        self.check_watching.start()

    @commands.command()
    async def set_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel where the messages will be sent."""
        self.channel_id = channel.id
        await ctx.send(f"Channel set to {channel.mention}")

    @commands.command()
    async def set_credentials(self, ctx, client_id, client_secret):
        """Set the Trakt API credentials."""
        await self.config.trakt_client_id.set(client_id)
        await self.config.trakt_client_secret.set(client_secret)
        await ctx.send("Trakt API credentials set")

    @tasks.loop(seconds=5)
    async def check_watching(self):
        trakt_client_id = await self.config.trakt_client_id()
        trakt_client_secret = await self.config.trakt_client_secret()

        if self.channel_id is not None and trakt_client_id is not None and trakt_client_secret is not None:
            await self.get_watching(trakt_client_id, trakt_client_secret)

    async def get_watching(self, client_id, client_secret):
        trakt.configuration.defaults.client(
            id=client_id,
            secret=client_secret,
            store=True
        )
        user = trakt.users.User("me")
        try:
            watched = user.watching(type="movie,episode")
            if watched and watched["watching"]:
                title = watched["watching"]["title"]
                if title != self.last_watched:
                    await self.bot.get_channel(self.channel_id).send(f"Now watching: {title}")
                    self.last_watched = title
        except (NotFoundException, TraktException):
            pass

    @check_watching.before_loop
    async def before_check_watching(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(rTrakt(bot))
