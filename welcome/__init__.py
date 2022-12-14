from .welcome import welcome

def setup(bot):
    cog = welcome(bot)
    bot.add_cog(cog)
