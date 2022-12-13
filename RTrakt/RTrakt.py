import discord
import requests
from redbot.core import commands
import trakt


class RTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trakt_client_id = "YOUR_TRAKT_CLIENT_ID"
        self.trakt_client_secret = "YOUR_TRAKT_CLIENT_SECRET"
        self.imdb_api_key = "API_KEY"

    @commands.command(help="Set the Trakt API client ID")
    async def settrakt(self, ctx, client_id: str):
        self.trakt_client_id = client_id

    @commands.command(help="Set the Trakt API client secret")
    async def setsecret(self, ctx, client_secret: str):
        self.trakt_client_secret = client_secret

    @commands.command(help="Set the IMDb API key")
    async def setimdb(self, ctx, api_key: str):
        self.imdb_api_key = api_key
        # Get the current user's Trakt account information
        user = trakt.users.me()

        # Get the currently playing media on the user's Trakt account
        playing = user.watching()

        # Search for the show or movie on IMDb
        query = playing.title
        endpoint = f"http://imdb-api.com/en/API/Search/k_{API_KEY}/s_{query}"
        response = requests.get(endpoint)
        data = response.json()

        # Get the poster image URL from the IMDb response
        poster_url = data["items"][0]["poster"]

        # Set the rich presence information
        game = discord.Game(name=playing.title, assets={
            "poster": poster_url
        })
        await self.bot.change_presence(activity=game)

def setup(bot):
    bot.add_cog(RTrakt(bot))
