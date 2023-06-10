from .rTrakt import rTrakt

def setup(bot):
    cog = rTrakt(bot)
    bot.add_cog(cog)
    return cog
