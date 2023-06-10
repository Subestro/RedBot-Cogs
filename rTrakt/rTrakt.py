import discord
import requests
from redbot.core import Config, commands
import asyncio
import aiohttp

TRAKT_API_URL = "https://api.trakt.tv"
TRAKT_AUTH_URL = "https://trakt.tv/oauth/token"

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Change the identifier to a unique value

        default_config = {
            "client_id": "",
            "client_secret": "",
            "channel_id": None,
            "access_token": "",
            "refresh_token": "",
            "expires_at": 0,
        }
        self.config.register_global(**default_config)

        self.session = aiohttp.ClientSession()
        self.background_task = self.bot.loop.create_task(self.check_trakt_activity())

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())
        self.background_task.cancel()

    async def check_trakt_activity(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            access_token = await self.config.access_token()
            refresh_token = await self.config.refresh_token()
            expires_at = await self.config.expires_at()

            if access_token and expires_at > asyncio.get_event_loop().time():
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                    "trakt-api-version": "2",
                }
                url = f"{TRAKT_API_URL}/sync/last_activities"

                try:
                    async with self.session.get(url, headers=headers) as response:
                        response.raise_for_status()

                        activities_data = await response.json()
                        if activities_data:
                            last_activity = activities_data[0]
                            last_activity_timestamp = last_activity.get("watched_at", 0)
                            stored_timestamp = await self.config.last_activity_timestamp()

                            if last_activity_timestamp > stored_timestamp:
                                await self.config.last_activity_timestamp.set(last_activity_timestamp)

                                if last_activity["type"] == "episode":
                                    show_title = last_activity["show"]["title"]
                                    season_number = last_activity["episode"]["season"]
                                    episode_number = last_activity["episode"]["number"]
                                    message = f"Currently watching: {show_title} - Season {season_number}, Episode {episode_number}"
                                    channel_id = await self.config.channel_id()
                                    channel = self.bot.get_channel(channel_id)
                                    if channel:
                                        await channel.send(message)

                except Exception as e:
                    error_message = f"An error occurred while checking Trakt activity: {e}"
                    channel_id = await self.config.channel_id()
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        await channel.send(error_message)

            # Wait for 5 seconds before checking again
            await asyncio.sleep(5)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.initialize_trakt()

    async def initialize_trakt(self):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
        }
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }

        try:
            async with self.session.post(TRAKT_AUTH_URL, headers=headers, json=data) as response:
                response.raise_for_status()
                auth_data = await response.json()
                access_token = auth_data.get("access_token")
                refresh_token = auth_data.get("refresh_token")
                expires_in = auth_data.get("expires_in")
                expires_at = asyncio.get_event_loop().time() + expires_in

                await self.config.access_token.set(access_token)
                await self.config.refresh_token.set(refresh_token)
                await self.config.expires_at.set(expires_at)

        except Exception as e:
            error_message = f"An error occurred while initializing Trakt: {e}"
            channel_id = await self.config.channel_id()
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(error_message)

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

def setup(bot):
    cog = rTrakt(bot)
    bot.add_cog(cog)
