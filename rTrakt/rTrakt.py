from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils import chat_formatting as cf
from trakt import Trakt

class rTrakt(commands.Cog):
    """Cog for Trakt integration."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = bot.get_cog("Config")

    async def get_current_watching_activity(self):
        try:
            trakt_config = await self.config.all()
            client_id = trakt_config.get("client_id")
            client_secret = trakt_config.get("client_secret")
            access_token = trakt_config.get("access_token")

            if client_id and client_secret and access_token:
                Trakt.configuration.defaults.client(
                    id=client_id,
                    secret=client_secret
                )
                Trakt.configuration.defaults.oauth.from_response_code(redirect_uri)
                Trakt.configuration.defaults.oauth.token = access_token
                Trakt.configuration.defaults.oauth.refresh()

                trakt = Trakt()
                trakt.sync.collection.get()
                watched = trakt['sync/playback'].get()
                if watched and watched.media_type == "episode":
                    return f"Watching {watched.show.title} - Season {watched.episode.season} Episode {watched.episode.number}"
                elif watched and watched.media_type == "movie":
                    return f"Watching {watched.movie.title}"
        except Exception as e:
            print(f"Error retrieving Trakt data: {e}")
        return "Playing Nothing"

    @commands.command()
    async def settraktcreds(self, ctx: commands.Context, client_id: str, client_secret: str):
        """Set Trakt API credentials."""
        try:
            await self.config.client_id.set(client_id)
            await self.config.client_secret.set(client_secret)
            await ctx.send(f"Trakt API credentials set successfully.")
        except Exception as e:
            await ctx.send(f"An error occurred while setting Trakt API credentials: {e}")

    @commands.command()
    async def settraktcode(self, ctx: commands.Context, code: str):
        """Set Trakt authorization code."""
        try:
            trakt_config = await self.config.all()
            client_id = trakt_config.get("client_id")
            client_secret = trakt_config.get("client_secret")
            redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

            if client_id and client_secret:
                Trakt.configuration.defaults.client(
                    id=client_id,
                    secret=client_secret
                )
                Trakt.configuration.defaults.oauth.from_response_code(redirect_uri)
                Trakt.configuration.defaults.oauth.token_exchange(code, redirect_uri)

                access_token = Trakt.configuration.defaults.oauth.token
                await self.config.access_token.set(access_token)

                await ctx.send("Trakt authorization code set successfully.")
            else:
                await ctx.send("Please set Trakt API credentials before authorizing the bot.")
        except Exception as e:
            await ctx.send(f"An error occurred while setting Trakt authorization code: {e}")

    @commands.command()
    async def traktstatus(self, ctx: commands.Context):
        """Show Trakt scrobbler status."""
        try:
            activity = await self.get_current_watching_activity()
            await ctx.send(cf.box(activity))
        except Exception as e:
            await ctx.send(f"An error occurred while retrieving Trakt scrobbler status: {e}")

    async def initialize(self):
        trakt_config = await self.config.all()
        client_id = trakt_config.get("client_id")
        client_secret = trakt_config.get("client_secret")

        if client_id and client_secret:
            Trakt.configuration.defaults.client(
                id=client_id,
                secret=client_secret
            )

            access_token = trakt_config.get("access_token")
            if access_token:
                Trakt.configuration.defaults.oauth.token = access_token
                Trakt.configuration.defaults.oauth.refresh()
