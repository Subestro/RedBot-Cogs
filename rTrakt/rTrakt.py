import discord
from redbot.core import commands, Config
from trakt import Trakt


class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2224567891)  # Replace with a unique identifier of your choice

        default_global = {
            "trakt_client_id": "",
            "trakt_client_secret": "",
            "trakt_access_token": "",
            "target_channel": None
        }

        self.config.register_global(**default_global)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.id != self.bot.user.id:
            return

        if before.activity != after.activity:
            await self.send_currently_watching(after.activity)

    async def send_currently_watching(self, activity):
        if isinstance(activity, discord.Streaming):
            trakt_access_token = await self.config.trakt_access_token()
            if trakt_access_token:
                Trakt.configuration.defaults.oauth.from_response(
                    response={"access_token": trakt_access_token}
                )

                if activity.name and activity.type == discord.ActivityType.streaming:
                    await self.config.target_channel.send(f"Currently watching: {activity.name}")


def setup(bot):
    cog = rTrakt(bot)
    bot.add_cog(cog)
