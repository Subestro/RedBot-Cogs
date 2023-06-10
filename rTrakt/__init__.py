from .rTrakt import rTrakt

def setup(bot):
    bot.add_cog(rTrakt(bot))
