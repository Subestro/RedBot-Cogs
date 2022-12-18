import requests
import discord
from discord.ext import commands

class FreeGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def freegames(self, ctx):
        # Get free games from Humble Bundle
        humble_url = "https://www.humblebundle.com/store/api/promotions?sort=discount_percent&direction=desc&page=0"
        r = requests.get(humble_url)
        humble_data = r.json()

        # Get free games from Epic Games
        epic_url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=es-ES&country=ES&allowCountries=ES"
        r = requests.get(epic_url)
        epic_data = r.json()

        # Build the message
        message = "Here are the current free games:\n\n"
        message += "**Humble Bundle**\n"
        for game in humble_data['data']:
            if game['discount_price']['amount'] == 0:
                embed = discord.Embed(title=game['human_name'], description=f"{game['regular_price']['amount']} {game['regular_price']['currency']}", color=0xff0000)
                embed.add_field(name="\u200b", value="Free")
                embed.set_thumbnail(url="https://www.humblebundle.com/static/humble_bundle_logo_small.png")
                embed.set_footer(text="Humble Bundle")
                await ctx.send(embed=embed)

        message += "\n**Epic Games**\n"
        for game in epic_data['data']['Catalog']['searchStore']['elements']:
            if game['price']['totalPrice']['discountPrice']['amount'] == 0:
                embed = discord.Embed(title=game['title'], description=f"{game['price']['totalPrice']['originalPrice']['amount']} {game['price']['totalPrice']['originalPrice']['currency']}", color=0xff0000)
                embed.add_field(name="\u200b", value="Free")
                embed.set_thumbnail(url="https://www.epicgames.com/fortnite/static/favicon.png")
                embed.set_footer(text="Epic Games")
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(FreeGames(bot))
