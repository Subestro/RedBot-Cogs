import discord
import requests
from redbot.core import commands, Config

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2224567891)  # Replace with a unique identifier of your choice

        default_global = {
            "trakt_client_id": "",
            "trakt_client_secret": "",
            "trakt_access_token": "",
            "target_channel_id": 0  # Replace with the actual channel ID where you want the message to be sent
        }

        self.config.register_global(**default_global)

    async def send_currently_watching(self, item):
        channel_id = await self.config.target_channel_id()
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(f"Currently watching: {item['title']}")
        else:
            print(f"Channel with ID {channel_id} not found.")

    @commands.command()
    async def traktid(self, ctx, client_id):
        await self.config.trakt_client_id.set(client_id)
        await ctx.send("Trakt client ID set successfully.")

    @commands.command()
    async def traktst(self, ctx, client_secret):
        await self.config.trakt_client_secret.set(client_secret)
        await ctx.send("Trakt client secret set successfully.")

    @commands.command()
    async def trakttoken(self, ctx, access_token):
        await self.config.trakt_access_token.set(access_token)
        await ctx.send("Trakt access token set successfully.")

    @commands.command()
    async def set_channel(self, ctx, channel: discord.TextChannel):
        await self.config.target_channel_id.set(channel.id)
        await ctx.send(f"Target channel set to {channel.mention}.")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Check if the user's activity has changed
        if before.activity != after.activity and isinstance(after.activity, discord.Streaming):
            access_token = await self.config.trakt_access_token()
            if access_token:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
                response = requests.get("https://api.trakt.tv/users/me/watching", headers=headers)
                if response.status_code == 200:
                    watching_item = response.json()
                    await self.send_currently_watching(watching_item)
                else:
                    print(f"Trakt API request failed with status code {response.status_code}.")
            else:
                print("Trakt access token not set.")

def setup(bot):
    bot.add_cog(rTrakt(bot))
