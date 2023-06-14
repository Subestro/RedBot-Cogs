import discord
from redbot.core import commands, Config
from trakt import Trakt

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Use a unique identifier

        default_guild_settings = {
            'client_id': None,
            'client_secret': None
        }

        self.config.register_guild(**default_guild_settings)

    @commands.command()
    async def trakt(self, ctx):
        guild_settings = await self.config.guild(ctx.guild).all()

        if not guild_settings['client_id'] or not guild_settings['client_secret']:
            await ctx.send("Trakt client ID or secret not set. Use the `settrakt` command to set them.")
            return

        Trakt.configuration.defaults.client(
            id=guild_settings['client_id'],
            secret=guild_settings['client_secret'],
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        Trakt.configuration.defaults.oauth.from_response(
            input('Enter the pin given at %s : ' % Trakt['oauth'].authorize_url())
        )
        movie = Trakt['search'].movie('The Matrix')[0]
        await ctx.send(f"Watching {movie.title} on {movie.year}.")

    @commands.command()
    @commands.guild_only()
    @commands.admin()
    async def settrakt(self, ctx, client_id: str, client_secret: str):
        await self.config.guild(ctx.guild).client_id.set(client_id)
        await self.config.guild(ctx.guild).client_secret.set(client_secret)
        await ctx.send("Trakt client ID and secret set successfully.")

    @commands.Cog.listener()
    async def on_ready(self):
        print("rTrakt cog is ready.")

def setup(bot):
    bot.add_cog(rTrakt(bot))
