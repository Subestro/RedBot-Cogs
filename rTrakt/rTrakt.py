import discord
from discord.ext import commands
import aiohttp
import asyncio
from redbot.core.data_manager import basic_config

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.config = basic_config.BasicConfig("rTrakt", {"access_token": "", "refresh_token": "", "api_key": ""})
        self.update_presence_task = asyncio.create_task(self.update_presence())
    
    @commands.command()
    async def rTraktAuth(self, ctx):
        auth_url = "https://trakt.tv/oauth/authorize?client_id=<client_id>&redirect_uri=<redirect_uri>&response_type=code"
        embed = discord.Embed(title="Trakt API Authorization", description="Click the link below to authorize the Trakt API for your account. Once you have authorized the API, enter the code in the command to complete the process.", color=discord.Color.blue())
        embed.add_field(name="Authorization Link", value=auth_url)
        embed.set_footer(text="This link will expire in 10 minutes.")
        await ctx.send(embed=embed)
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=600.0)
        except asyncio.TimeoutError:
            await ctx.send("Authorization timed out. Please try again.")
            return
        
        async with self.session.post("https://api.trakt.tv/oauth/token", data={
            "code": msg.content,
            "client_id": "<client_id>",
            "client_secret": "<client_secret>",
            "redirect_uri": "<redirect_uri>",
            "grant_type": "authorization_code"
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
                details="Trakt Scrobbler",
                large_image="large_image_name",  # name of the large image asset
                large_image_url=poster_url,
                small_image="small_image_name",  # name of the small image asset
                small_image_url=poster_url
            )
            
            # Set the rich presence
            await self.bot.change_presence(activity=presence)
            
            await asyncio.sleep(300)
