import discord
import aiohttp
import asyncio
from redbot.core import commands
from redbot.core.data_manager import basic_config

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.config = basic_config.BasicConfig("rTrakt", {"access_token": "", "refresh_token": "", "api_key": ""})
        self.update_presence_task = asyncio.create_task(self.update_presence())
    
    @commands.command()
    async def rTraktAuth(self, ctx, code: str):
        async with self.session.post("https://api.trakt.tv/oauth/token", json={
            "client_id": "your_client_id",  # replace with your Trakt API client ID
            "client_secret": "your_client_secret",  # replace with your Trakt API client secret
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "authorization_code",
            "code": code
        }) as resp:
            data = await resp.json()
            access_token = data["access_token"]
            refresh_token = data["refresh_token"]
        
        self.config["access_token"] = access_token
        self.config["refresh_token"] = refresh_token
        await ctx.send("Authorization successful!")
    
    @commands.command()
    async def rOMDB(self, ctx, api_key: str):
        self.config["api_key"] = api_key
        await ctx.send("OMDB API key set successfully!")
    
    async def update_presence(self):
        try:
            access_token = self.config["access_token"]
            api_key = self.config["api_key"]
        except KeyError:
            return
        
        while True:
            # Make a GET request to the Trakt API to get the currently playing item
            async with self.session.get("https://api.trakt.tv/users/me/watching", headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }) as resp:
                data = await resp.json()
                item = data["item"]
                title = item["title"]
                year = item["year"]
            
            # Make a GET request to the OMDB API to get the poster image
            async with self.session.get(f"http://www.omdbapi.com/?apikey={api_key}&t={title}&y={year}") as resp:
                data = await resp.json()
                poster_url = data["Poster"]
            
            # Create the rich presence object with the poster image
            presence = discord.RichPresence(
                state=f"Watching {title} ({year})",
            # Create the rich presence object with the poster image
            presence = discord.RichPresence(
                state=f"Watching {title} ({year})",
                details="Trakt Scrobbler",
                large_image="poster",
                large_image_url=poster_url
            )

            # Set the bot's rich presence
            await self.bot.change_presence(activity=presence)

            # Sleep for 5 minutes before updating the presence again
            await asyncio.sleep(300)
