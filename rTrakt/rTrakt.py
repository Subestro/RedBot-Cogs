import discord
import requests
from redbot.core import commands
import trakt
import configparser

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trakt_client_id = None
        self.trakt_client_secret = None
        self.omdb_api_key = None
        self.trakt_redirect_url = None
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None

        # Read the configuration values from a file
        config = configparser.ConfigParser()
        config.read('rTrakt_config.ini')
        if 'trakt' in config:
            self.trakt_client_id = config['trakt'].get('client_id', None)
            self.trakt_client_secret = config['trakt'].get('client_secret', None)
            self.trakt_redirect_url = config['trakt'].get('redirect_url', None)
            self.access_token = config['trakt'].get('access_token', None)
            self.refresh_token = config['trakt'].get('refresh_token', None)
            self.expires_at = config['trakt'].get('expires_at', None)
        if 'omdb' in config:
            self.omdb_api_key = config['omdb'].get('api_key', None)

    @commands.command(help="Set the Trakt API client ID")
    async def Rsettrakt(self, ctx, client_id: str):
        self.trakt_client_id = client_id
        # Save the client ID to the configuration file
        config = configparser.ConfigParser()
        config.read('rTrakt_config.ini')
        if 'trakt' not in config:
            config['trakt'] = {}
        config['trakt']['client_id'] = client_id
        with open('rTrakt_config.ini', 'w') as configfile:
            config.write(configfile)

    @commands.command(help="Set the Trakt API client secret")
    async def Rsetsecret(self, ctx, client_secret: str):
        self.trakt_client_secret = client_secret
        # Save the client secret to the configuration file
        config = configparser.ConfigParser()
        config.read('rTrakt_config.ini')
        if 'trakt' not in config:
            config['trakt'] = {}
        config['trakt']['client_secret'] = client_secret
        with open('rTrakt_config.ini', 'w') as configfile:
            config.write(configfile)

    @commands.command(help="Set the Trakt API redirect URL")
    async def Rsetredirect(self, ctx, redirect_url: str):
        self.trakt_redirect_url = redirect_url
        # Save the redirect URL to the configuration file
        config = configparser.ConfigParser()
        config.read('rTrakt_config.ini')
        if 'trakt' not in config:
            config['trakt'] = {}
        config['trakt']['redirect_url'] = redirect_url
        with open('rTrakt_config.ini', 'w') as configfile:
            config.write(configfile)

    @commands.command(help="Set the OMDb API key")
    async def Rsetomdb(self, ctx, api_key: str):
        self.omdb_api_key = api_key
        # Save the API key to the configuration file
        config = configparser.ConfigParser()
        config.read('rTrakt_config.ini')
        if 'omdb' not in config:
            config['omdb'] = {}
        config['omdb']['api_key'] = api_key
        with open('rTrakt_config.ini', 'w') as configfile:
            config.write(configfile)

    @commands.command(help="Authorize the bot to access your Trakt account")
    async def Rauthorize(self, ctx):
        # Build the authorization URL
        auth_url = trakt.users.oauth.get_authorize_url(client_id=self.trakt_client_id, redirect_uri=self.trakt_redirect_url)

        # Send the authorization URL to the user
        await ctx.send(f"Please visit the following URL to authorize the bot to access your Trakt account: {auth_url}")

        # Wait for the user to enter the authorization code
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=300)
        except asyncio.TimeoutError:
            await ctx.send("Timed out waiting for authorization code.")
            return

        # Exchange the authorization code for an access token
        code = msg.content
        token = trakt.users.oauth.token_exchange(client_id=self.trakt_client_id, client_secret=self.trakt_client_secret, redirect_uri=self.trakt_redirect_url, code=code)

        # Save the access token, refresh token, and expiration time to the configuration file
        config = configparser.ConfigParser()
        config.read('rTrakt_config.ini')
        if 'trakt' not in config:
            config['trakt'] = {}
        config['trakt']['access_token'] = token['access_token']
        config['trakt']['refresh_token'] = token['refresh_token']
        config['trakt']['expires_at'] = str(token['expires_at'])
        with open('rTrakt_config.ini', 'w') as configfile:
            config.write(configfile)

        await ctx.send("Successfully authorized the bot to access your Trakt account.")

    @commands.command(help="Get the currently playing show or movie on your Trakt account")
    async def Rplaying(self, ctx):
        # Read the access token and expiration time from the configuration file
        config = configparser.ConfigParser()
        config.read('rTrakt_config.ini')
        access_token = config['trakt'].get('access_token', None)
        refresh_token = config['trakt'].get('refresh_token', None)
        expires_at = config['trakt'].get('expires_at', None)

        # Check if the access token has expired
        if expires_at is not None and datetime.fromisoformat(expires_at) < datetime.now():
            # Refresh the access token
            token = trakt.users.oauth.token_refresh(client_id=self.trakt_client_id, client_secret=self.trakt_client_secret, redirect_uri=self.trakt_redirect_url, refresh_token=refresh_token)
            access_token = token['access_token']
            refresh_token = token['refresh_token']
            expires_at = token['expires_at']

            # Save the refreshed access token and expiration time to the configuration file
            config = configparser.ConfigParser()
            config.read('rTrakt_config.ini')
            if 'trakt' not in config:
                config['trakt'] = {}
            config['trakt']['access_token'] = access_token
            config['trakt']['refresh_token'] = refresh_token
            config['trakt']['expires_at'] = str(expires_at)
            with open('rTrakt_config.ini', 'w') as configfile:
                config.write(configfile)

        # Set the access token for the Trakt API client
        trakt.core.OAUTH_TOKEN = access_token

        # Get the current user's Trakt account information
        user = trakt.users.me()

        # Get the currently playing media on the user's Trakt account
        playing = user.watching()

        # Search for the show or movie on OMDb
        query = playing.title
        endpoint = f"http://www.omdbapi.com/?apikey={self.omdb_api_key}&s={query}"
        response = requests.get(endpoint)
        data = response.json()

        # Get the poster image URL from the OMDb response
        poster_url = data["Search"][0]["Poster"]

        # Build the embed message
        embed = discord.Embed(title=f"Currently watching: {playing.title}")
        embed.set_thumbnail(url=poster_url)
        embed.add_field(name="Type", value=playing.type.capitalize())
        embed.add_field(name="Season", value=playing.season)
        embed.add_field(name="Episode", value=playing.episode)
        embed.add_field(name="Progress", value=f"{playing.progress}%")
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(rTrakt(bot))

       
