import requests
from bs4 import BeautifulSoup
from redbot.core import commands

class FreeGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_current_free_game(self):
        # Make an HTTP GET request to the "Free Game" section of the Epic Store website
        url = "https://store.epicgames.com/en-US/"
        response = requests.get(url)

        # Parse the HTML content of the response
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the element containing the current free game information
        free_game_element = soup.find("div", class_="FrontpageFreeGame-sc-1rv5z5d-0 fjrIxl")

        # Extract the name and release date of the current free game
        name = free_game_element.find("h3").text
        release_date = free_game_element.find("div", class_="FrontpageFreeGame__EndDate-sc-1rv5z5d-2 kBwIHW").text

        return (name, release_date)
    
    @commands.command()
    async def current_free_game(self, ctx):
        name, release_date = self.get_current_free_game()
        await ctx.send(f"The current free game on the Epic Store is {name}, available until {release_date}.")

def setup(bot):
    bot.add_cog(FreeGames(bot))
