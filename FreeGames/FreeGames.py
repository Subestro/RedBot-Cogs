import discord
import time
import requests
from redbot.core import commands, checks, Config

class FreeGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_global = {"last_free_game_check": 0}
        self.config.register_global(**default_global)

    @commands.command()
    async def fgc(self, ctx):
        """Checks if there is a free game available on Epic Games."""
        # Make a request to the Epic Games API to get the list of free games
        response = requests.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=es-ES&country=ES&allowCountries=ES")

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response data to get the list of free games
            free_games = response.json()

            if isinstance(free_games, list) and free_games:  # If free_games is a non-empty list
                # Extract the name and price information for the first free game from the list
                game_data = free_games[0]
                if "name" in game_data and "price" in game_data:  # If the game data has a "name" and "price" key
                    game_name = game_data["name"]
                    original_price = game_data["price"]
                    current_price = 0  # Free games have a current price of 0

                    # Create the embed object
                    embed = discord.Embed(title=f"**{game_name}**")
                    # Set the original price field
                    embed.add_field(name="Original price", value=f"~~{original_price}~~", inline=True)
                    # Set the current price field
                    embed.add_field(name="Current price", value=f"**{current_price}**", inline=True)

                    await ctx.send(embed=embed)
                else:
                    # If the game data is missing a "name" or "price" key, handle the error
                    print("Invalid game data: missing name or price key")
                    return
            else:  # If free_games is not a list or is an empty list
                message = "There are no free games available on Epic Games right now."
                await ctx.send(message)
        else:
            # If the request was not successful, handle the error
            print(f"API request failed with status code {response.status_code}")
            return

    @commands.command()
    @checks.is_owner()
    async def fgcnotify(self, ctx):
        """Checks for new free games on Epic Games and sends a notification to the configured channel."""
        # First, get the current time
        current_time = time.time()
        
        # Next, get the last time we checked for free games from the config
        last_free_game_check = await self.config.last_free_game_check()
        
        # Check if it's been more than 24 hours since the last time we checked for free games
        if current_time - last_free_game_check > 86400:  # 86400 seconds = 24 hours
            # If it has been more than 24 hours, update the last_free_game_check time in the config
            await self.config.last_free_game_check.set(current_time)
            
            # Make a request to the Epic Games API to get the list of free games
            response = requests.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=es-ES&country=ES&allowCountries=ES")
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the response data to get the list of free games
                # The exact way to do this will depend on the structure of the data returned by the API
                # You may need to refer to the API documentation or use a JSON parsing library to extract the data you need
                free_games = response.json()
                
                # Loop through the list of free games and send a notification for each one
                for free_game in free_games:
                    # Get the channel to send the notification to from the config
                    notification_channel_id = await self.config.notification_channel()
                    notification_channel = self.bot.get_channel(notification_channel_id)
                    
                    # Create the message content
                    message_content = f"A new free game is available on Epic Games: {free_game['name']}"
                    
                    # Send the notification
                    await notification_channel.send(message_content)
            else:
                # If the request was not successful, handle the error
                print(f"API request failed with status code {response.status_code}")
                return
        else:
            # If it hasn't been more than 24 hours since the last time we checked, do nothing
            pass