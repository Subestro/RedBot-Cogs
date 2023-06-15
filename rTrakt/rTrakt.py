import discord
import asyncio
from redbot.core import commands, checks, Config
import trakt

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567111)  # Replace with a unique identifier
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
            await asyncio.sleep(5)  # Check every 5s

    async def get_current_watching_activity(self):
        try:
            trakt_config = await self.config.all()
            client_id = await trakt_config.client_id()
            client_secret = await trakt_config.client_secret()
            access_token = await trakt_config.access_token()

            if client_id and client_secret and access_token:
                trakt.core.AUTH_METHOD = trakt.OAuthAuthenticator(client_id, client_secret, access_token)
                watched = await trakt.sync.watched_movies()
                if watched:
                    return f"Watching {watched[0].movie.title}"
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
        await ctx.send(f"Please authorize the bot using the following link:\n\n{await self.get_authorization_url()}")

    async def get_authorization_url(self):
        trakt_config = await self.config.all()
        client_id = await trakt_config.client_id()
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        return f"https://trakt.tv/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"

    @commands.command()
    @checks.is_owner()
    async def settrakttoken(self, ctx, authorization_code: str):
        trakt_config = await self.config.all()
        client_id = await trakt_config.client_id()
        client_secret = await trakt_config.client_secret()
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

        try:
            trakt.core.AUTH_METHOD = trakt.OAuthAuthenticator(client_id, client_secret)
            response = await trakt.core.AUTH_METHOD.get_access_token(authorization_code, redirect_uri)
            access_token = response.get("access_token")
            if access_token:
                await self.config.access_token.set(access_token)
                await ctx.send("Trakt access token has been set.")
            else:
                await ctx.send("Failed to exchange authorization code for access token.")
        except Exception as e:
            await ctx.send(f"Failed to exchange authorization code for access token: {e}")

    @commands.command()
    @checks.is_owner()
    async def setactivity(self, ctx, *, activity: str):
        await self.update_bot_activity(activity)
        await ctx.send(f"Activity set to: {activity}")

def setup(bot):
    bot.add_cog(rTrakt(bot))
