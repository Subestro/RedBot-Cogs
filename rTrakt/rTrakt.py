import json
import discord
import requests
from redbot.core import Config, commands

TRAKT_API_URL = "https://api.trakt.tv"
RICH_PRESENCE_ACTIVITY_TYPE = 2  # Watching

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Change the identifier to a unique value

        default_config = {
            "client_id": "",
            "client_secret": "",
            "channel_id": None,
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

    @commands.command()
    @commands.is_owner()
    async def set_trakt_channel(self, ctx, channel: discord.TextChannel):
        await self.config.channel_id.set(channel.id)
        await ctx.send(f"Trakt channel has been set to {channel.mention} and saved.")

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
        url = f"{TRAKT_API_URL}/sync/playback"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            playback_data = response.json()
            if playback_data:
                current_item = playback_data[0]
                channel_id = await self.config.channel_id()
                channel = self.bot.get_channel(channel_id)
                if channel:
                    message = f"Currently watching: {current_item['title']} ({current_item['year']})"
                    await channel.send(message)

                    # Update rich presence with the currently playing item
                    await self.update_rich_presence(current_item)

    async def update_rich_presence(self, current_item):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {client_secret}",
        }
        data = {
            "pid": 1,  # Rich presence ID (choose any unique integer)
            "activity": {
                "details": current_item["title"],
                "timestamps": {"start": current_item["progress"]},
                "assets": {"large_image": current_item["type"]},
            },
        }
        self.bot.http.request(
            discord.http.Route("POST", f"/v8/applications/{client_id}/rich-presence/{RICH_PRESENCE_ACTIVITY_TYPE}"),
            headers=headers,
            json=data,
        )

def setup(bot):
    cog = rTrakt(bot)
    bot.add_cog(cog)
