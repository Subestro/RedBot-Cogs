from .FreeGamesChecker import FreeGamesChecker

def setup(bot):
    cog = FreeGamesChecker(bot)
    bot.add_cog(cog)