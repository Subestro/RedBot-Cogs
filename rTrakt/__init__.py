from .rtrakt import rTrakt

def setup(bot):
    cog = rTrakt(bot)
    bot.add_cog(cog)
