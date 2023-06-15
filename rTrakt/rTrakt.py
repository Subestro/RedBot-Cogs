import discord
from discord.ext import commands
from redbot.core import Config
from redbot.core.bot import Red

# Make sure you have the trakt module installed via pip
import trakt

class rTrakt(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)

        # Set default configuration values
        default_guild_settings = {
            "channel_id": None,
            "trakt_access_token": None,
            "trakt_refresh_token": None
        }
        self.config.register_guild(**default_guild_settings)

        # Start the task to update the currently watching activity
        self.update_activity.start()

    def cog_unload(self):
        # Stop the task when the cog is unloaded
        self.update_activity.cancel()

    async def get_currently_watching(self, access_token):
        # Retrieve the currently watching information from Trakt using the access token
        trakt.init(access_token)
        user = trakt.users.User('me')
        watched_movies = user.watched_movies(pagination=True)
        currently_watching = next(watched_movies)

        return currently_watching

    async def get_access_token(self, code):
        # Exchange the authorization code for an access token
        auth = trakt.TraktAuth()
        access_token = await auth.exchange_code_for_access_token(code, redirect_uri='urn:ietf:wg:oauth:2.0:oob')

        return access_token['access_token'], access_token['refresh_token']

    @commands.Cog.listener()
    async def on_ready(self):
        print("rTrakt is ready.")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Check if the member is the bot itself
        if after.id != self.bot.user.id:
            return

        # Check if the activity type is "watching"
        if after.activity and after.activity.type == discord.ActivityType.watching:
            # Get the guild-specific Trakt access token
            guild = after.guild
            access_token = await self.config.guild(guild).trakt_access_token()

            if access_token:
                currently_watching = await self.get_currently_watching(access_token)

                # Get the guild-specific channel to send the activity updates
                channel_id = await self.config.guild(guild).channel_id()

                if channel_id:
                    channel = guild.get_channel(channel_id)
                    if channel:
                        await channel.send(f"{after.display_name} is now watching: {currently_watching.title}")

    @tasks.loop(minutes=15)  # Adjust the interval as per your requirement
    async def update_activity(self):
        # Get the guilds the bot is in
        guilds = self.bot.guilds

        for guild in guilds:
            # Get the guild-specific channel to send the activity updates
            channel_id = await self.config.guild(guild).channel_id()

            if channel_id:
                channel = guild.get_channel(channel_id)

                # Get the guild-specific Trakt access token
                access_token = await self.config.guild(guild).trakt_access_token()

                if access_token:
                    currently_watching = await self.get_currently_watching(access_token)

                    if channel:
                        await self.bot.change_presence(activity=discord.Activity(
                            type=discord.ActivityType.watching, name=currently_watching.title), guild=guild)

                        await channel.send(f"{self.bot.user.display_name} is now watching: {currently_watching.title}")

    @commands.command()
    @commands.guild_only()
    async def set_activity_channel(self, ctx, channel: discord.TextChannel):
        # Set the guild-specific channel to receive the activity updates
        await self.config.guild(ctx.guild).channel_id.set(channel.id)
        await ctx.send(f"Activity updates will now be sent to {channel.mention}.")

    @commands.command()
    async def authenticate(self, ctx):
        # Generate the Trakt OAuth authorization URL
        auth = trakt.TraktAuth()
        auth_url = auth.get_authorization_url(redirect_uri='urn:ietf:wg:oauth:2.0:oob')

        await ctx.send(f"Visit the following URL to authorize the bot: {auth_url}")

    @commands.command()
    async def set_access_token(self, ctx, code):
        # Exchange the authorization code for an access token
        access_token, refresh_token = await self.get_access_token(code)

        # Store the access token and refresh token in the guild-specific config
        await self.config.guild(ctx.guild).trakt_access_token.set(access_token)
        await self.config.guild(ctx.guild).trakt_refresh_token.set(refresh_token)

        await ctx.send("Access token and refresh token have been set.")

def setup(bot: Red):
    cog = rTrakt(bot)
    bot.add_cog(cog)
