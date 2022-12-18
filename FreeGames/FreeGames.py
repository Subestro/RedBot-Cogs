from redbot.core import commands
import discord
import requests

class FreeGames(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def checkfreegames(self, ctx):
    # Make a request to the Epic Games API to get a list of free games
    epic_games_response = requests.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=es-US&country=US&allowCountries=US")
    epic_games_data = epic_games_response.json()

    # Make a request to the Humble Bundle API to get a list of games on sale
    humble_bundle_response = requests.get("https://www.humblebundle.com/store/api/search?sort=discount&filter=onsale&request=1")
    humble_bundle_data = humble_bundle_response.json()

    # You'll need to figure out how to get a list of free games from the Uplay API.
    # Once you have that data, you can store it in a variable called "uplay_data"

    # Create an empty list to store the names of the free games
    free_games = []

    # Iterate through the list of games from the Epic Games API
    for game in epic_games_data:
      # Check if the game is free
      if game['price']['totalPrice']['discountPrice'] == 0:
        # If the game is free, add its name to the list of free games
        free_games.append(game['title'])

    # Iterate through the list of games from the Humble Bundle API
    for game in humble_bundle_data:
      # Check if the game is free
      if game['salePrice']['amount'] == 0:
        # If the game is free, add its name to the list of free games
        free_games.append(game['title'])

    # Iterate through the list of games from the Uplay API
    for game in uplay_data:
      # Check if the game is free
      if game['price']['amount'] == 0:
        # If the game is free, add its name to the list of free games
        free_games.append(game['title'])

    # If there are no free games, do nothing
    if len(free_games) == 0:
      await ctx.send("There are no free games currently available on Humble, Epic Games, or Uplay.")
      return

    # If there are free games, create an embed message
    embed = discord.Embed(title="Free Games Alert!", description="There are currently free games available on Humble, Epic Games, and Uplay!", color=discord.Color.red())
    embed.add_field(name="Free Games", value="\n".join(free_games), inline=False)

    # Send the embed message to the channel where the command was used
    await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(FreeGames(bot))
