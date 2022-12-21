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
        self.imdb_api_key = None

        # Read the configuration values from a file
        config = configparser.ConfigParser()
        config.read('rTrakt_config.ini')
        if 'trakt' in config:
            self.trakt_client_id = config['trakt'].get('client_id', None)
            self.trakt_client_secret = config['trakt'].get('client_secret', None)
        if 'imdb' in config:
            self.imdb_api_key = config['imdb'].get('api_key', None)

    @commands.command(help="Set the Trakt API client ID")
    async def settrakt(self, ctx, client_id: str):
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
    async def setsecret(self, ctx, client_secret: str):
        self.trakt_client_secret = client_secret
        # Save the client secret to the configuration file
        config = configparser.ConfigParser()
        config.read('rTrakt_config.ini')
        if 'trakt' not in config:
            config['trakt'] = {}
        config['trakt']['client_secret'] = client_secret
        with open('rTrakt_config.ini', 'w') as configfile:
            config.write(configfile)

    @commands.command(help="Set the IMDb API key")
    async def setimdb(self, ctx, api_key: str):
        self.imdb_api_key = api_key
        # Save the API key to the configuration file
        config = configparser.ConfigParser()
        config.read('rTrakt_config.ini')
        if 'imdb' not in config:
            config['imdb'] = {}
        config['imdb']['api_key'] = api_key
        with open('rTrakt_config.ini', 'w') as configfile:
            config.write(configfile)

        # Get the current user's Trakt account information
        user = trakt.users.me()

        # Get the currently playing media on the user's Trakt account
        playing = user.watching()

        # Search for the show or movie on IMDb
        query = playing.title
        endpoint = f"http://imdb-api.com/en/API/Search/k_{self.imdb_api_key}/s_{query}"
        response = requests.get(endpoint)
        data = response.json()

        # Get the poster image URL from the IMDb response
        poster_url = data["items"][0]["poster"]

        # Set the rich presence information
        game = discord.Game(name=playing.title, assets={
            "poster": poster_url
        })
        await self.bot.change_presence(activity=game)

