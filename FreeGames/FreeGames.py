import discord
import requests
from requests.exceptions import HTTPError, Timeout
from redbot.core import commands, config
import asyncio

class Game:
    def __init__(self, name, url, poster_url, free_until):
        self.name = name
        self.url = url
        self.poster_url = poster_url
        self.free_until = free_until
        

class FreeGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SERVICE_NAME = "Epic Games"
        self.MODULE_ID = "epic"
        self.AUTHOR = "Default"
        self.URL = "https://www.epicgames.com/store/us-US/product/"
        self.ENDPOINT = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
        self.free_games_channel_id = None  # Initialize the channel ID to None

        # Set up the config settings for the cog
        default_global = {
            "free_games_channel_id": None
        }
        self.config = config.Config.get_conf(self, identifier=283472984728934, force_registration=True)
        self.config.register_global(**default_global)

    @commands.command()
    async def set_free_games_channel(self, ctx, channel: discord.TextChannel):
        """Sets the channel where free games will be announced."""
        # Store the channel ID in the config
        await self.config.free_games_channel_id.set(channel.id)
        await ctx.send(f"Free games will now be announced in {channel.mention}.")

    async def check_for_free_games(self):
        """Periodically checks for new free games and sends a message if any are found."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            free_games = self.process_request(self.make_request())
            if free_games:
                # Retrieve the channel ID from the config
                channel_id = await self.config.free_games_channel_id()
                channel = self.bot.get_channel(channel_id)
                for game in free_games:
                    embed = discord.Embed(title=game.name, color=0x00FFFF)
                    embed.set_thumbnail(url="https://raw.githubusercontent.com/Subestro/RedBot-Cogs/development/FreeGames/Epic_Store_Logo.png")
                    embed.description = f"**Free** until {game.free_until}"
                    embed.add_field(name="Get Now", value=game.url, inline=True)
                    embed.set_image(url=game.poster_url)
                    await channel.send(embed=embed)
            await asyncio.sleep(3600)  # Check for new games every hour

    @commands.command()
    async def get_free_games(self, ctx):
        free_games = self.process_request(self.make_request())

        if not free_games:
            await ctx.send("There are no free games available at this time.")
            return

        embed = discord.Embed(title="Free Games", color=0x00FFFF)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/Subestro/RedBot-Cogs/development/FreeGames/Epic_Store_Logo.png")
        for game in free_games:
            embed.add_field(name=game.name, value=f"Free until: **{game.original_price}**\nGet now: {game.url}", inline=False)
            embed.set_image(url=game.poster_url)
        await ctx.send(embed=embed)
