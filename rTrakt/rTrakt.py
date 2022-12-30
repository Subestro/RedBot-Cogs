import discord
import aiohttp
import asyncio
from redbot.core import commands, Config, checks
from redbot.core.utils.chat_formatting import box
from redbot.core.data_manager import bundled_data_path

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=8462457310, force_registration=True)
        default_global = {
            "client_id": None,
            "client_secret": None,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "access_token": None,
            "refresh_token": None,
        }
        self.config.register_global(**default_global)

        self.update_presence_task = self.bot.loop.create_task(self.update_presence())

    async def update_presence(self):
        """Periodically update the bot's rich presence with the current scrobbler information."""
        while not self.bot.is_closed():
            client_id = await self.config.client_id()
            client_secret = await self.config.client_secret()
            access_token = await self.config.access_token()
            if client_id and client_secret and access_token:
                await set_trakt_scrobbler_presence(client_id, client_secret, access_token)
            # Update the rich presence every 5 minutes
            await asyncio.sleep(300)

    @commands.group(name="trakt")
    @checks.is_owner()
    async def _trakt(self, ctx):
        """Manage the Trakt scrobbler for the bot's rich presence."""
        pass

    @_trakt.command(name="generatecodes")
    async def trakt_generatecodes(self, ctx):
        """Generate the client ID and client secret for the Trakt API."""
        # Replace this with the actual code for generating the client ID and client secret
        client_id = "YOUR_CLIENT_ID_HERE"
        client_secret = "YOUR_CLIENT_SECRET_HERE"
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)
        await ctx.send(f"Client ID: {client_id}\nClient secret: {client_secret}")

    @_trakt.command(name="displaycode")
    async def trakt_displaycode(self, ctx):
        """Display the client ID and client secret for the Trakt API."""
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        if not client_id or not client_secret:
            await ctx.send("The client ID and client secret have not been set yet. Use the `generatecodes` command to generate them.")
        else:
            await ctx.send(f"Client ID: {client_id}\nClient secret: {client_secret}")


    @_trakt.command(name="pollauth")
    async def trakt_pollauth(self, ctx):
        """Poll for authorization to access the Trakt API."""
        client_id = await self.config.client_id()
        redirect_uri = await self.config.redirect_uri()
        # Replace this with the actual code for polling for authorization
        await ctx.send(f"Visit the following URL to authorize the bot to access your Trakt account:\n\nhttps://trakt.tv/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}")

    @_trakt.command(name="successauth")
    async def trakt_successauth(self, ctx, access_token: str, refresh_token: str):
        """Store the access and refresh tokens for the Trakt API."""
        await self.config.access_token.set(access_token)
        await self.config.refresh_token.set(refresh_token)
        await ctx.send("Successfully authorized the bot to access your Trakt account.")


async def set_trakt_scrobbler_presence(bot, client_id, client_secret, access_token):
    async with aiohttp.ClientSession() as session:
        # Retrieve the current scrobbler information from the Trakt API
        async with session.get("https://api.trakt.tv/sync/last_activities", headers={
            "Content-Type": "application/json",
            "trakt-api-key": client_id,
            "trakt-api-version": "2",
            "Authorization": f"Bearer {access_token}",
        }) as resp:
            if resp.status == 200:
                data = await resp.json()
                # Extract the relevant scrobbler information from the response
                scrobbler_type = data["scrobbles"]["movie"]["last_activity_at"]
                scrobbler_title = data["scrobbles"]["movie"]["last_watched_at"]
                scrobbler_episode = data["scrobbles"]["episode"]["last_watched_at"]
                if scrobbler_type == "movie":
                    # Retrieve the movie's runtime from the Trakt API
                    async with session.get(f"https://api.trakt.tv/movies/{scrobbler_title}", headers={
                        "Content-Type": "application/json",
                        "trakt-api-key": client_id,
                        "trakt-api-version": "2",
                        "Authorization": f"Bearer {access_token}",
                    }) as resp:
                        if resp.status == 200:
                            movie_data = await resp.json()
                            runtime = movie_data["runtime"]
                            # Set the rich presence to show the movie that is currently being scrobbled, including the runtime
                            presence = discord.Activity(name=scrobbler_title, type=discord.ActivityType.watching, details=f"{runtime} minutes")
                            await bot.change_presence(activity=presence)
                        else:
                            print(f"Error retrieving movie information: {resp.status} {await resp.text()}")
                elif scrobbler_type == "episode":
                    # Retrieve the TV show's runtime from the Trakt API
                    async with session.get(f"https://api.trakt.tv/shows/{scrobbler_title}", headers={
                        "Content-Type": "application/json",
                        "trakt-api-key": client_id,
                        "trakt-api-version": "2",
                                                "Authorization": f"Bearer {access_token}",
                    }) as resp:
                        if resp.status == 200:
                            show_data = await resp.json()
                            runtime = show_data["runtime"]
                            # Set the rich presence to show the TV show and episode that is currently being scrobbled, including the runtime
                            presence = discord.Activity(name=scrobbler_title, type=discord.ActivityType.watching, details=f"{scrobbler_episode} | {runtime} minutes")
                            await bot.change_presence(activity=presence)
                        else:
                            print(f"Error retrieving show information: {resp.status} {await resp.text()}")
            else:
                print(f"Error retrieving scrobbler information: {resp.status} {await resp.text()}")

def setup(bot):
    bot.add_cog(rTrakt(bot))


