from .errorlogs import Errorlogs

def setup(bot):
    bot.add_cog(Errorlogs(bot))
