import discord
from discord.ext import commands
from trakt import Trakt

class TraktCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client_id = 'YOUR_TRAKT_CLIENT_ID'
        self.client_secret = 'YOUR_TRAKT_CLIENT_SECRET'

    def authenticate(self):
        Trakt.configuration.defaults.client(
            id=self.client_id,
            secret=self.client_secret
        )

    @commands.command()
    async def search_movie(self, ctx, movie_title):
        self.authenticate()
        results = Trakt['search'].movie(query=movie_title)
        if results:
            movie = results[0]
            await ctx.send(f"Title: {movie.title}\nYear: {movie.year}")
        else:
            await ctx.send('No movie found.')

    @commands.command()
    async def search_show(self, ctx, show_title):
        self.authenticate()
        results = Trakt['search'].show(query=show_title)
        if results:
            show = results[0]
            await ctx.send(f"Title: {show.title}\nYear: {show.year}")
        else:
            await ctx.send('No show found.')

def setup(bot):
    bot.add_cog(TraktCog(bot))
