import discord
from redbot.core import commands
import requests

class FreeGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def checkfreegames(self, ctx):
        # Use the API link to get the list of free games
        r = requests.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=es-US&country=US&allowCountries=US")
        data = r.json()

        # Check if there are any free games available
        if data['data']['promotions']:
            # Create the embed message
            embed = discord.Embed(title="Free Games on Epic Games Store", color=0xff0000)

            # Add the list of free games to the embed message
            for game in data['data']['promotions']:
                embed.add_field(name=game['title'], value=game['description'], inline=False)
                # Set the game's name as the title of the embed message
                embed.title = game['title']
                # Set the game's poster as the footer of the embed message
                embed.set_footer(text=game['keyImages'][0]['url'])

            # Send the embed message to the channel
            await ctx.send(embed=embed)
        else:
            await ctx.send("There are no free games available on the Epic Games Store at the moment.")

def setup(bot):
    bot.add_cog(FreeGames(bot))
