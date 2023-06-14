from .rTrakt import rTrakt

async def setup(bot):
    cog = rTrakt(bot)
    await cog.initialize()  # Add an initialize method if necessary
    bot.add_cog(cog)

