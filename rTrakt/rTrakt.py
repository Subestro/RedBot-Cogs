import discord
from discord.ext import commands
from trakt import Trakt
from redbot.core import Config

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_global = {
            "client_id": None,
            "client_secret": None
        }
        self.config.register_global(**default_global)

    @commands.command()
    async def trakt(self, ctx):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        if not client_id or not client_secret:
            await ctx.send("Please set the Trakt API client ID and secret using the `settrakt` command.")
            return
        Trakt.configuration.defaults.client(
            id=client_id,
            secret=client_secret,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        Trakt.configuration.defaults.oauth.from_response(
            input('Enter the pin given at %s : ' % Trakt['oauth'].authorize_url())
        )
        movie = Trakt['search'].movie('The Matrix')[0]
        await ctx.send(f"Watching {movie.title} on {movie.year}.")

    @commands.command()
    async def settrakt(self, ctx, client_id: str, client_secret: str):
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)
        await ctx.send("Trakt API client ID and secret set.")

def setup(bot):
    cog = rTrakt(bot)
    bot.add_cog(cog)
