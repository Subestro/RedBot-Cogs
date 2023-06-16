import discord
from redbot.core import commands
import trakt

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trakt_client = None

    @commands.Cog.listener()
    async def on_red_ready(self):
        # Initialize Trakt client
        self.trakt_client = trakt.Trakt("4129a600893f2b057301ef356e96277f0bf2898c205ff02e6dcfdeecef899b42", "be487ee7080112b005cd8008157eceb022a14740e7f10bbc6c571803893dbda5")

    @commands.command()
    async def check_credentials(self, ctx):
        if self.trakt_client is None:
            await ctx.send("Trakt credentials not set up.")
            return

        try:
            user = self.trakt_client.user("me").get()
            await ctx.send("Trakt credentials are valid.")
        except trakt.errors.AuthenticationError:
            await ctx.send("Invalid Trakt credentials.")
        except trakt.errors.NotFoundException:
            await ctx.send("Trakt user not found.")

def setup(bot):
    bot.add_cog(rTrakt(bot))
