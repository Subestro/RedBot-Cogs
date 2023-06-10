from .rTrakt import rTraktCog

def setup(bot):
    bot.add_cog(rTraktCog(bot))
