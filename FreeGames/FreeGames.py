import discord
from redbot.core import commands
import requests

class FreeGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def freegame(self, ctx):
        # Send a GET request to the URL
        response = requests.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=es-US&country=US&allowCountries=US")

        # Check if the request was successful
        if response.status_code == 200:
            # Retrieve the data from the response
            data = response.json()

            # Get the name of the free game
            game_name = data["data"]["Catalog"]["searchStore"]["elements"][0]["title"]["displayValue"]

            # Create an embed message with the free game information
            embed = discord.Embed(title=f"Current free game: {game_name}", color=discord.Color.green())
            embed.set_thumbnail(url=data["data"]["Catalog"]["searchStore"]["elements"][0]["keyImages"][0]["url"])
            embed.add_field(name="Description", value=data["data"]["Catalog"]["searchStore"]["elements"][0]["description"]["displayValue"], inline=False)
            embed.set_footer(text="Information provided by Epic Games Store")

            # Send the embed message
            await ctx.send(embed=embed)
        else:
            # If the request was not successful, send an error message
            await ctx.send("An error occurred while retrieving the free game information.")

def setup(bot):
    bot.add_cog(FreeGames(bot))
