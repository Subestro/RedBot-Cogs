import discord
import asyncio
from redbot.core import commands, checks, Config
import trakt

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
            client_id = await trakt_config.client_id()
            client_secret = await trakt_config.client_secret()
            access_token = await trakt_config.access_token()

            if client_id and client_secret and access_token:
                trakt.init(client_id=client_id, client_secret=client_secret, oauth=True)
                trakt.set_default_client()
                trakt.configuration.defaults.oauth.from_response_code(code=access_token)

                watched = await trakt.users(username='me').watched()
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

    def get_authorization_url(self):
        trakt_config = await self.config.all()
        client_id = await trakt_config.client_id()
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        return f"https://trakt.tv/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"

    @commands.command()
    @checks.is_owner()
    async def settraktcreds(self, ctx, client_id: str, client_secret: str):
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)
        await ctx.send(f"Please authorize the bot using the following link:\n\n{self.get_authorization_url()}")

    @commands.command()
    @checks.is_owner()
    async def setactivity(self, ctx, *, activity: str):
        await self.update_bot_activity(activity)
        await ctx.send(f"Activity set to: {activity}")

def setup(bot):
    bot.add_cog(rTrakt(bot))
