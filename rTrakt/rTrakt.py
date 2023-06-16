import discord
from redbot.core import commands, Config
import requests
import trakt

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Replace with a unique identifier
        self.config.register_global(client_id=None, client_secret=None, access_token=None, refresh_token=None)
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

        self.trakt_client = trakt.init(client_id=client_id, client_secret=client_secret, access_token=access_token, refresh_token=refresh_token)

    @commands.Cog.listener()
    async def on_red_ready(self):
        try:
            await self.initialize_trakt_client()
        except commands.CommandError as e:
            print(e)

    @commands.command()
    async def check_credentials(self, ctx):
        try:
            await self.initialize_trakt_client()
            user = self.trakt_client.users.get()
            await ctx.send("Trakt credentials are valid.")
        except trakt.errors.AuthenticationException:
            await ctx.send("Invalid Trakt credentials.")
        except trakt.errors.NotFoundException:
            await ctx.send("Trakt user not found.")
        except commands.CommandError as e:
            await ctx.send(str(e))

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
        auth = trakt.init(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
        auth_token = auth.exchange_pin(pin)
        return auth_token['access_token'], auth_token['refresh_token']

def setup(bot):
    bot.add_cog(rTrakt(bot))
