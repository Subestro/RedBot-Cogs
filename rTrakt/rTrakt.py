import discord
import requests
from redbot.core import Config, commands
import asyncio

TRAKT_API_URL = "https://api.trakt.tv"

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Change the identifier to a unique value

        default_config = {
            "client_id": "",
            "client_secret": "",
            "channel_id": None,
            "last_activity_timestamp": 0,
        }
        self.config.register_global(**default_config)

        self.background_task = self.bot.loop.create_task(self.check_trakt_activity())

    def cog_unload(self):
        self.background_task.cancel()

    async def check_trakt_activity(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            client_id = await self.config.client_id()
            client_secret = await self.config.client_secret()
            headers = {
                "Content-Type": "application/json",
                "trakt-api-key": client_id,
                "trakt-api-version": "2",
            }
            url = f"{TRAKT_API_URL}/sync/last_activities"

            try:
                response = await self.bot.session.get(url, headers=headers)  # Await the HTTP request
                response.raise_for_status()  # Raise an exception if the request is not successful

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
            "trakt-api-key": client_id,
            "trakt-api-version": "2",
        }
        url = f"{TRAKT_API_URL}/sync/last_activities"

        try:
            response = await self.bot.session.get(url, headers=headers)  # Await the HTTP request
            response.raise_for_status()  # Raise an exception if the request is not successful

            activities_data = await response.json()
            if activities_data:
                last_activity = activities_data[0]
                last_activity_timestamp = last_activity.get("watched_at", 0)
                await self.config.last_activity_timestamp.set(last_activity_timestamp)

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
