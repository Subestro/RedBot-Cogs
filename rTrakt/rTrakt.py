import discord
from redbot.core import commands, Config
import requests
import trakt
import asyncio

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567000)  # Replace with a unique identifier
        self.config.register_global(client_id=None, client_secret=None, access_token=None, refresh_token=None)
        self.trakt_client = None
        self.channel_id = None
        self.check_task = None

    async def initialize_trakt_client(self):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        access_token = await self.config.access_token()
        refresh_token = await self.config.refresh_token()

        if client_id is None or client_secret is None:
            raise commands.CommandError("Trakt credentials not set up.")

        if access_token is None or refresh_token is None:
            raise commands.CommandError("Trakt tokens not set up.")

        trakt.Trakt.configuration.defaults.client(
            id=client_id,
            secret=client_secret,
            access_token=access_token,
            refresh_token=refresh_token
        )

        self.trakt_client = trakt.Trakt()

    async def check_scrobbler(self):
        while True:
            try:
                await self.initialize_trakt_client()
                user = self.trakt_client.users("me").get()
                watching = await self.get_watching_status(user)
                if watching is not None:
                    await self.send_watching_info(watching)
            except Exception as e:
                print(str(e))
            await asyncio.sleep(5)

    async def get_watching_status(self, user):
        headers = {
            'Content-Type': 'application/json',
            'trakt-api-version': '2',
            'trakt-api-key': client_id
        }
        url = f"https://api.trakt.tv/users/{user.ids.slug}/watching"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    async def send_watching_info(self, watching):
        if watching["type"] == "episode":
            media_title = watching["show"]["title"]
        elif watching["type"] == "movie":
            media_title = watching["movie"]["title"]
        else:
            media_title = "Unknown"

        if media_title and self.channel_id is not None:
            channel = self.bot.get_channel(self.channel_id)
            await channel.send(f"I'm currently watching: {media_title}")

    @commands.Cog.listener()
    async def on_red_ready(self):
        try:
            await self.initialize_trakt_client()
            self.check_task = self.bot.loop.create_task(self.check_scrobbler())
        except commands.CommandError as e:
            print(e)

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
        access_token, refresh_token = self.exchange_pin_for_tokens(client_id, client_secret, redirect_uri, pin)
        if access_token and refresh_token:
            await self.config.access_token.set(access_token)
            await self.config.refresh_token.set(refresh_token)
            await ctx.send("Trakt tokens have been set.")
        else:
            await ctx.send("Token exchange failed. Please check the PIN.")

    def exchange_pin_for_tokens(self, client_id, client_secret, redirect_uri, pin):
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
    async def set_watching_channel(self, ctx, channel_id):
        self.channel_id = int(channel_id)
        await ctx.send(f"The channel has been set to: {self.channel_id}")

def setup(bot):
    bot.add_cog(rTrakt(bot))
