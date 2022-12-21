import discord
from redbot.core import commands
import trakt

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def set_trakt_keys(self, ctx, client_id: str, client_secret: str, access_token: str):
        """Sets the Trakt API keys and access token."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        await ctx.send("Trakt API keys and access token set successfully!")

    @commands.command()
    async def update_presence(self, ctx):
        # Authenticate with the Trakt Scrobbler API
        trakt.init(self.client_id, self.client_secret)
        access_token = trakt.auth.oauth(self.access_token)

        # Retrieve the details of the currently-playing media
        scrobble_state = trakt.sync.scrobble.state(access_token)

        # Create a rich presence object based on the media type
        if scrobble_state.type == "episode":
            game = discord.Game(name=f"{scrobble_state.show.title} - S{scrobble_state.episode.season}E{scrobble_state.episode.number} - {scrobble_state.episode.title}", type=discord.ActivityType.watching)
        elif scrobble_state.type == "movie":
            game = discord.Game(name=f"{scrobble_state.movie.title}", type=discord.ActivityType.watching)

        # Update the bot's rich presence
        await self.bot.change_presence(activity=game)
