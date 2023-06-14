import discord
from redbot.core import commands
from trakt.core import Trakt

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def trakt(self, ctx):
        Trakt.configuration.defaults.client(
            id='YOUR_CLIENT_ID',
            secret='YOUR_CLIENT_SECRET',
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        Trakt.configuration.defaults.oauth.from_response(
            input('Enter the pin given at %s : ' % Trakt['oauth'].authorize_url())
        )
        movie = Trakt['search'].movie('The Matrix')[0]
        await ctx.send(f"Watching {movie.title} on {movie.year}.")

    @commands.Cog.listener()
    async def on_ready(self):
        print("rTrakt cog is ready.")

def setup(bot):
    bot.add_cog(rTrakt(bot))
