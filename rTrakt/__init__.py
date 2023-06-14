from .rTrakt import rTrakt

async def setup(bot):
    cog = rTrakt(bot)
    await cog.initialize()
    bot.add_cog(cog)
