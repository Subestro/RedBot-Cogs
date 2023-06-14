import discord
from discord.ext import commands
from redbot.core import Config
import trakt


class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567991)  # Use a unique identifier
        self.config.register_global(api_key=None)

    async def update_presence(self, activity):
        await self.bot.change_presence(activity=activity)

    @commands.Cog.listener()
    async def on_ready(self):
        trakt.Trakt.configuration.defaults.client(
            id='4129a600893f2b057301ef356e96277f0bf2898c205ff02e6dcfdeecef899b42',
            secret='be487ee7080112b005cd8008157eceb022a14740e7f10bbc6c571803893dbda5',
        )
        activity = discord.Activity(name="Initializing...", type=discord.ActivityType.watching)
        await self.update_presence(activity)

    @commands.command()
    @commands.guild_only()
    async def set_watching(self, ctx):
        api_key = await self.config.api_key()
        trakt.Trakt.configuration.defaults.client(
            id='4129a600893f2b057301ef356e96277f0bf2898c205ff02e6dcfdeecef899b42',
            secret='be487ee7080112b005cd8008157eceb022a14740e7f10bbc6c571803893dbda5',
        )
        trakt.Trakt.configuration.defaults.oauth.from_response(flow='device', refresh=True, store=True)
        trakt.Trakt.configuration.defaults.http = trakt.Trakt.HTTPClient(headers={'trakt-api-key': api_key})

        activity = discord.Activity(name="Loading...", type=discord.ActivityType.watching)
        await self.update_presence(activity)

        try:
            auth = trakt.Trakt['oauth'].device_code(device='default')  # Use 'default' as the device name
            print(f"Go to {auth.verification_url} and enter code: {auth.user_code}")
            await ctx.send(f"Go to {auth.verification_url} and enter the code provided in console.")
            await auth.poll()
            items = await trakt.Trakt['sync'].watched_movies()
            if items:
                watched_movie = items[0]['movie']['title']
                activity = discord.Activity(name=watched_movie, type=discord.ActivityType.watching)
                await self.update_presence(activity)
                await ctx.send(f"Now watching: {watched_movie}")
            else:
                await ctx.send("No movies being watched currently.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")


def setup(bot):
    bot.add_cog(rTrakt(bot))
