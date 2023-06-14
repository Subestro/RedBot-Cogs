from .rTrakt import rTrakt

async def setup(bot):
    cog = rTrakt(bot)
    bot.add_cog(cog)

