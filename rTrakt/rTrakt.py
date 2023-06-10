import json
import discord
import requests
from redbot.core import Config, commands

TRAKT_API_URL = "https://api.trakt.tv"
RICH_PRESENCE_ACTIVITY_TYPE = 2  # Watching

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=123332890)  # Change the identifier to a unique value

        default_config = {
            "client_id": "",
            "client_secret": "",
        }
        self.config.register_global(**default_config)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        await self.setup_rich_presence()

    async def setup_rich_presence(self):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {client_secret}",
        }
        data = {
            "pid": 1,  # Rich presence ID (choose any unique integer)
            "activity": {
                "details": "Not watching anything",
                "timestamps": {"start": 0},
                "assets": {"large_image": "default"},
            },
        }
        await self.bot.http.request(
            discord.http.Route("POST", f"/v8/applications/{client_id}/rich-presence/{RICH_PRESENCE_ACTIVITY_TYPE}"),
            headers=headers,
            json=data,
        )

    @commands.command()
    @commands.is_owner()
    async def set_trakt_secrets(self, ctx, client_id: str, client_secret: str):
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)
        await ctx.send("Trakt secrets have been set and saved.")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before == self.bot.user and before.activities != after.activities:
            for activity in after.activities:
                if (
                    isinstance(activity, discord.CustomActivity)
                    and activity.name == "Watching"
                    and activity.type == discord.ActivityType.streaming
                ):
                    await self.send_trakt_message(activity)

    async def send_trakt_message(self, activity):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        headers = {
            "Content-Type": "application/json",
            "trakt-api-key": client_id,
            "trakt-api-version": "2",
        }
        url = f"{TRAKT_API_URL}/sync/playback/stop"
        payload = {
            "progress": 100,
            "episode": {"ids": {"trakt": activity.episode_id}},
            "movie": {"ids": {"trakt": activity.movie_id}},
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            channel = self.bot.get_channel(YOUR_CHANNEL_ID)  # Replace with your #general channel ID
            if channel:
                await channel.send(f"Currently watching: {activity.details}")

def setup(bot):
    bot.add_cog(rTrakt(bot))
