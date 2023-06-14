from redbot.core import commands, Config
from trakt import Trakt

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2224567891)  # Replace with a unique identifier of your choice

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

    @commands.group()
    async def trakt(self, ctx):
        """Trakt API settings"""
        pass

    @trakt.command()
    async def id(self, ctx, client_id):
        """Set the Trakt client ID"""
        await self.config.trakt_client_id.set(client_id)
        await ctx.send("Trakt client ID has been set.")

    @trakt.command()
    async def st(self, ctx, client_secret):
        """Set the Trakt client secret"""
        await self.config.trakt_client_secret.set(client_secret)
        await ctx.send("Trakt client secret has been set.")

    @commands.command()
    async def search_movie(self, ctx, *, movie_title):
        await self.initialize()
        results = Trakt['search'].query('movies', movie_title)
        if results:
            movie = results[0]
            await ctx.send(f"Title: {movie.title}\nYear: {movie.year}")
        else:
            await ctx.send('No movie found.')

    @commands.command()
    async def search_show(self, ctx, *, show_title):
        await self.initialize()
        results = Trakt['search'].query('shows', show_title)
        if results:
            show = results[0]
            await ctx.send(f"Title: {show.title}\nYear: {show.year}")
        else:
            await ctx.send('No show found.')

def setup(bot):
    bot.add_cog(rTrakt(bot))
