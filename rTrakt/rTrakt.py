import discord
from redbot.core import commands, Config
import requests
import trakt
import asyncio
from trakt.errors import NotFoundException, TraktException

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567000)  # Replace with a unique identifier
        self.config.register_global(client_id=None, client_secret=None, access_token=None, refresh_token=None)
        self.trakt_client = None
        asyncio.create_task(self.initialize_trakt_client())  # Call the function as a task

    async def initialize_trakt_client(self):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        access_token = await self.config.access_token()
        refresh_token = await self.config.refresh_token()

        if client_id is None or client_secret is None:
            raise commands.CommandError("Trakt credentials not set up.")

        if access_token is None or refresh_token is None:
            raise commands.CommandError("Trakt tokens not set up.")

        self.trakt_client = trakt.Trakt(client_id, client_secret, access_token, refresh_token)

    @commands.Cog.listener()
    async def on_red_ready(self):
        self.start_periodic_check()

    def start_periodic_check(self):
        interval_seconds = 10  # Adjust the interval as desired (in seconds)
        self.bot.loop.create_task(self.periodic_check(interval_seconds))

    async def periodic_check(self, interval_seconds):
        while True:
            await self.check_watching()
            await asyncio.sleep(interval_seconds)

    async def check_watching(self):
        try:
            user = trakt.users.User("me")
            watching = user.watching()
            if watching is not None:
                await self.send_watching_status(watching.title)
        except NotFoundException:
            print("Trakt user not found.")
        except TraktException:
            print("Invalid Trakt credentials.")

    async def send_watching_status(self, show_title):
        channel_id = await self.config.channel_id()
        if channel_id is not None:
            channel = self.bot.get_channel(channel_id)
            await channel.send(f"Currently watching: {show_title}")

    @commands.command()
    @commands.is_owner()
    async def set_client_credentials(self, ctx, client_id, client_secret):
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)
        auth_url = f"https://trakt.tv/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
        await ctx.send(f"Trakt client credentials have been set. Authorize the application using this link:\n{auth_url}")

    @commands.command()
    @commands.is_owner()
    async def set_pin(self, ctx, pin):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        access_token, refresh_token = await self.exchange_pin_for_tokens(client_id, client_secret, redirect_uri, pin)
        if access_token and refresh_token:
            await self.config.access_token.set(access_token)
            await self.config.refresh_token.set(refresh_token)
            await ctx.send("Trakt tokens have been set.")

    @commands.command()
    @commands.is_owner()
    async def set_channel(self, ctx, channel: discord.TextChannel):
        await self.config.channel_id.set(channel.id)
        await ctx.send(f"Watching status messages will be sent to {channel.mention}")

def setup(bot):
    cog = rTrakt(bot)
    bot.add_cog(cog)
