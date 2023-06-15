import discord
import asyncio
from redbot.core import commands, checks, Config
from trakt import Trakt

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Replace with a unique identifier
        self.config.register_global(
            client_id=None,
            client_secret=None,
            access_token=None,
            activity=""
        )

        self.task = bot.loop.create_task(self.update_activity())

    def cog_unload(self):
        self.task.cancel()

    async def update_activity(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            activity = await self.get_current_watching_activity()
            await self.update_bot_activity(activity)
            await asyncio.sleep(300)  # Check every 5 minutes

    async def get_current_watching_activity(self):
        try:
            trakt_config = await self.config.all()
            client_id = trakt_config["client_id"]
            client_secret = trakt_config["client_secret"]
            access_token = trakt_config["access_token"]

            if client_id and client_secret and access_token:
                Trakt.configuration.defaults.client(
                    id=client_id,
                    secret=client_secret
                )
                trakt = Trakt(access_token=access_token)
                watched = await trakt['sync/watched'].movies()
                if watched:
                    return f"Watching {watched[0].title}"
        except Exception as e:
            print(f"Error retrieving Trakt data: {e}")
        return "Playing Nothing"

    async def update_bot_activity(self, activity):
        await self.config.activity.set(activity)
        if activity:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))
        else:
            await self.bot.change_presence(activity=None)

    @commands.command()
    @checks.is_owner()
    async def settraktcreds(self, ctx, client_id: str, client_secret: str):
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)
        await ctx.send("Trakt API credentials have been set.")
        await ctx.send(f"Please authorize the bot using the following link:\n\n{await self.get_authorization_url()}")

    @commands.command()
    @checks.is_owner()
    async def setaccesstoken(self, ctx, code: str):
        trakt_config = await self.config.all()
        client_id = trakt_config["client_id"]
        client_secret = trakt_config["client_secret"]
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

        Trakt.configuration.defaults.client(
            id=client_id,
            secret=client_secret
        )

        token = await Trakt['oauth'].token_exchange(code, redirect_uri=redirect_uri)
        access_token = token['access_token']

        await self.config.access_token.set(access_token)
        await ctx.send("Trakt access token has been set.")
        await ctx.send(f"Please check your Trakt connected apps section to verify the rTrakt app.")

    @commands.command()
    @checks.is_owner()
    async def setactivity(self, ctx, *, activity: str):
        await self.update_bot_activity(activity)
        await ctx.send(f"Activity set to: {activity}")

    async def get_authorization_url(self):
        trakt_config = await self.config.all()
        client_id = trakt_config["client_id"]
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        auth = Trakt['oauth'].authorize_url(client_id, redirect_uri=redirect_uri)
        return auth

def setup(bot):
    bot.add_cog(rTrakt(bot))
