import discord
from redbot.core import commands, Config
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

        trakt.core.CLIENT_ID = client_id
        trakt.core.CLIENT_SECRET = client_secret
        trakt.core.OAUTH_TOKEN = access_token
        trakt.core.OAUTH_REFRESH_TOKEN = refresh_token
        self.trakt_client = trakt.Trakt()

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
            user = self.trakt_client.user("me").get()
            await ctx.send("Trakt credentials are valid.")
        except trakt.errors.AuthenticationError:
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
    async def set_tokens(self, ctx, access_token, refresh_token):
        await self.config.access_token.set(access_token)
        await self.config.refresh_token.set(refresh_token)
        await ctx.send("Trakt tokens have been set.")

def setup(bot):
    bot.add_cog(rTrakt(bot))
