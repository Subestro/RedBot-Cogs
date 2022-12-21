import discord
import requests
from redbot.core import commands
import trakt
import configparser

class RTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trakt_client_id = None
        self.trakt_client_secret = None
        self.omdb_api_key = None
        self.trakt_redirect_uri = None

        # Read the configuration values from a file
        config = configparser.ConfigParser()
        config.read('rTrakt_config.ini')
        if 'trakt' in config:
            self.trakt_client_id = config['trakt'].get('client_id', None)
            self.trakt_client_secret = config['trakt'].get('client_secret', None)
            self.trakt_redirect_uri = config['trakt'].get('redirect_uri', None)
        if 'omdb' in config:
            self.omdb_api_key = config['omdb'].get('api_key', None)

        # Initialize the Trakt API with the client ID and client secret
        trakt.init(client_id=self.trakt_client_id, client_secret=self.trakt_client_secret)

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

    @commands.command(help="Set the Trakt API redirect URI")
    async def Rsetredirect(self, ctx, redirect_uri: str):
        self.trakt_redirect_uri = redirect_uri
        # Save the redirect URI to the configuration file
        config = configparser.ConfigParser()
        config.read('rTrakt_config.ini')
        if 'trakt' not in config:           
            config['trakt'] = {}
        config['trakt']['redirect_uri'] = redirect_uri
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

    @commands.command(help="Get the currently playing media on the user's Trakt account")
    async def Rplaying(self, ctx):
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

        # Send a message to the Discord channel with the poster image and information about the currently playing media
        message = f"Currently watching: {playing.title} ({playing.year})\nRating: {playing.rating}\n{poster_url}"
        await ctx.send(message)
