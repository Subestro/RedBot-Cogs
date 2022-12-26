import discord
import json
import requests
from requests.exceptions import HTTPError, Timeout
from redbot.core import commands
import asyncio

class Game:
    def __init__(self, name, url, poster_url, original_price):
        self.name = name
        self.url = url
        self.poster_url = poster_url
        self.original_price = original_price
        

class FreeGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SERVICE_NAME = "Epic Games"
        self.MODULE_ID = "epic"
        self.AUTHOR = "Default"
        self.URL = "https://www.epicgames.com/store/us-US/product/"
        self.ENDPOINT = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
        self.free_games_channel_id = None  # Initialize the channel ID to None

    @commands.command()
    async def set_free_games_channel(self, ctx, channel: discord.TextChannel):
        """Sets the channel where free games will be announced."""
        self.free_games_channel_id = channel.id
        await ctx.send(f"Free games will now be announced in {channel.mention}.")

    async def check_for_free_games(self):
        """Periodically checks for new free games and sends a message if any are found."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            free_games = self.process_request(self.make_request())
            if free_games:
                channel = self.bot.get_channel(self.free_games_channel_id)
                for game in free_games:
                    embed = discord.Embed(title=game.name, color=0x00FFFF)
                    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Epic_games_store_logo.svg/800px-Epic_games_store_logo.svg.png")
                    embed.description = f"~~${game.original_price}~~ |**Free**"
                    embed.add_field(name="Get Now", value=game.url, inline=True)
                    embed.set_image(url=game.poster_url)
                    await channel.send(embed=embed)
            await asyncio.sleep(3600)  # Check for new games every hour

    @commands.command()
    async def get_free_games(self, ctx):
        def make_request():
            """Makes the request and removes the unnecessary JSON data."""
            try:
                raw_data = requests.get(self.ENDPOINT)
                raw_data = json.loads(raw_data.content)  # Bytes to json object
                raw_data = raw_data["data"]["Catalog"]["searchStore"]["elements"]  # Cleans the data
                return raw_data
            except (HTTPError, Timeout, requests.exceptions.ConnectionError, TypeError):
                logger.error(f"Request to {self.SERVICE_NAME} by module '{self.MODULE_ID}' failed")
                return False

        def process_request(raw_data):
            """Returns a list of free games from the raw data."""
            processed_data = []

            if not raw_data:
                return False
            try:
                for i in raw_data:
                    # (i["price"]["totalPrice"]["discountPrice"] == i["price"]["totalPrice"]["originalPrice"]) != 0
                    try:
                        if i["promotions"]["promotionalOffers"]:
                            original_price = i["price"]["totalPrice"].get("originalPrice", 0)
                            game = Game(i["title"], str(self.URL + i["productSlug"]), i["keyImages"][1]["url"], original_price)
                            processed_data.append(game)
                    except TypeError:  # This gets executed when ["promotionalOffers"] is empty or does not exist
                        pass
            except KeyError:
                logger.exception(f"Data from module '{self.MODULE_ID}' couldn't be processed")

            return processed_data

        # Get the list of free games
        free_games = process_request(make_request())

        # Send the list of free games in an embed
        if free_games:
            for game in free_games:
                embed = discord.Embed(title=game.name, color=0x00FFFF)
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Epic_games_store_logo.svg/800px-Epic_games_store_logo.svg.png")
                embed.description = f"~~${game.original_price}~~ |**Free**"
                embed.add_field(name="Get Now", value=game.url, inline=True)
                embed.set_image(url=game.poster_url)
                await ctx.send(embed=embed)
        else:
            await ctx.send("No free games could be found.")

