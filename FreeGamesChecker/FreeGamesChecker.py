import discord
from discord.ext import commands
import requests

class FreeGamesCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.free_games = []
        self.channel = None

    @commands.command()
    async def start_free_games_notifications(self, ctx, channel: discord.TextChannel):
        self.channel = channel
        await ctx.send("Free games notifications enabled!")

    @commands.command()
    async def stop_free_games_notifications(self, ctx):
        self.channel = None
        await ctx.send("Free games notifications disabled!")

    @commands.command()
    async def test_free_games_notifications(self, ctx):
        if self.channel:
            await ctx.send("Free games notifications are enabled and working!")
        else:
            await ctx.send("Free games notifications are disabled or not set up.")

    @commands.Cog.listener()
    async def on_ready(self):
        # Retrieve a list of free games from the Epic Store API
        epic_response = requests.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US")
        epic_games = epic_response.json()

        # Retrieve a list of free games from the Steam API
        steam_response = requests.get("http://api.steampowered.com/ISteamApps/GetAppList/v2")
        steam_games = steam_response.json()['applist']['apps']

        # Filter the Steam games to only include those that are marked as free
        steam_free_games = [game for game in steam_games if game['price_overview']['discount_percent'] == 100]

        # Retrieve a list of free games from the Uplay API
        uplay_response = requests.get("https://public-ubiservices.ubi.com/v3/products/offers?platformType=uplay&country=US&language=en-US")
        uplay_games = uplay_response.json()['offers']

        # Filter the Uplay games to only include those that are marked as free
        uplay_free_games = [game for game in uplay_games if game['price']['finalPrice'] == 0]

        # Combine the lists of free games from Epic, Steam, and Uplay
        games = epic_games + steam_free_games + uplay_free_games

        # Check if any new games have become free since the last check
        new_free_games = [game for game in games if game['title'] not in self.free_games]

        # If there are any new free games, send a message to the configured channel
        if new_free_games:
            message = "New free games:\n"
            for game in new_free_games:
                # Get the rating and price of the game
                rating = game.get('rating', 'N/A')
                price = game.get('price', 'Free')
                message += f"- {game['title']} ({rating}/100) - {price}\n"
            await self.channel.send(message)

        # Update the list of free games
        self.free_games = [game['title'] for game in games]
               
