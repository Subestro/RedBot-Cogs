from redbot.core import commands, Config
from trakt import Trakt

class TraktCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Replace with a unique identifier of your choice

        default_global = {
            "trakt_client_id": "",
            "trakt_client_secret": ""
        }

        self.config.register_global(**default_global)

    async def initialize(self):
        trakt_client_id = await self.config.trakt_client_id()
        trakt_client_secret = await self.config.trakt_client_secret()

        Trakt.configuration.defaults.client(
            id=trakt_client_id,
            secret=trakt_client_secret
        )

    @commands.command()
    async def search_movie(self, ctx, movie_title):
        await self.initialize()
        results = Trakt['search'].movie(query=movie_title)
        if results:
            movie = results[0]
            await ctx.send(f"Title: {movie.title}\nYear: {movie.year}")
        else:
            await ctx.send('No movie found.')

    @commands.command()
    async def search_show(self, ctx, show_title):
        await self.initialize()
        results = Trakt['search'].show(query=show_title)
        if results:
            show = results[0]
            await ctx.send(f"Title: {show.title}\nYear: {show.year}")
        else:
            await ctx.send('No show found.')

def setup(bot):
    bot.add_cog(TraktCog(bot))
