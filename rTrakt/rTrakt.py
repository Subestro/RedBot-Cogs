import discord
from redbot.core import commands, Config
import trakt
from trakt.errors import NotFoundException, TraktException
import asyncio
import requests

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567000)  # Replace with a unique identifier
        self.config.register_global(client_id=None, client_secret=None, access_token=None, refresh_token=None, channel_id=None)
        self.trakt_client = None

    async def initialize_trakt_client(self):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        access_token = await self.config.access_token()
        refresh_token = await self.config.refresh_token()

        if client_id is None or client_secret is None:
            raise commands.CommandError("Trakt credentials not set up.")

        if access_token is None or refresh_token is None:
            raise commands.CommandError("Trakt tokens not set up.")

        self.trakt_client = trakt.Trakt()
        self.trakt_client.configuration.defaults.client(
            id=client_id,
            secret=client_secret,
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def send_watching_status(self, show_name):
        channel_id = await self.config.channel_id()
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            await channel.send(f"Currently watching: {show_name}")

    @commands.Cog.listener()
    async def on_red_ready(self):
        try:
            await self.initialize_trakt_client()
            await self.check_scrobbling_status()
            self.start_periodic_check()  # Start periodic checks
        except commands.CommandError as e:
            print(e)

    async def check_scrobbling_status(self):
        try:
            user = self.trakt_client.users.get("me")
            watching = user.watching()
            if watching is not None:
                await self.send_watching_status(watching.get("show").title)
        except NotFoundException:
            print("Trakt user not found.")
        except TraktException:
            print("Invalid Trakt credentials.")

    def start_periodic_check(self):
        interval_seconds = 10  # Adjust the interval as desired (in seconds)
        self.bot.loop.create_task(self.periodic_check(interval_seconds))

    async def periodic_check(self, interval_seconds):
        while True:
            await asyncio.sleep(interval_seconds)
            await self.check_scrobbling_status()

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
        else:
            await ctx.send("Token exchange failed. Please check the PIN.")

    async def exchange_pin_for_tokens(self, client_id, client_secret, redirect_uri, pin):
        token_url = 'https://trakt.tv/oauth/token'
        payload = {
            'code': pin,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }

        response = requests.post(token_url, data=payload)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            refresh_token = token_data['refresh_token']
            return access_token, refresh_token
        else:
            print(f"Token exchange failed with status code {response.status_code}")
            return None, None

    @commands.command()
    @commands.is_owner()
    async def set_watching_channel(self, ctx, channel: discord.TextChannel):
        await self.config.channel_id.set(channel.id)
        await ctx.send(f"Watching updates will be sent to the channel: {channel.mention}")

def setup(bot):
    bot.add_cog(rTrakt(bot))
