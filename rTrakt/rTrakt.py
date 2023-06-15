import discord
from discord.ext import commands
from redbot.core import commands, Config
import trakt


class rTrakt(commands.Cog):
    """Cog for interacting with the Trakt API."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_global = {"client_id": None, "client_secret": None}
        self.config.register_global(**default_global)
        
    async def get_trakt_client(self):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        if not client_id or not client_secret:
            raise Exception("Trakt API credentials are not set.")
        trakt.core.oauth.OAuth.default_client(
            id=client_id,
            secret=client_secret
        )
        return trakt

    @commands.group(autohelp=True)
    async def trakt(self, ctx):
        """Interact with Trakt API."""
        pass

    @trakt.command()
    async def settraktcreds(self, ctx: commands.Context, client_id: str, client_secret: str):
        """Set Trakt API credentials."""
        try:
            await self.config.client_id.set(client_id)
            await self.config.client_secret.set(client_secret)
            await ctx.send("Trakt API credentials set successfully.")
        except Exception as e:
            await ctx.send(f"An error occurred while setting Trakt API credentials: {e}")

    @trakt.command()
    async def authorize(self, ctx: commands.Context):
        """Authorize the bot with Trakt."""
        try:
            trakt_client = await self.get_trakt_client()
            auth_url = trakt_client['oauth'].authorization_url('urn:ietf:wg:oauth:2.0:oob')
            await ctx.send(f"Please authorize the bot using the following link:\n\n{auth_url}")
        except Exception as e:
            await ctx.send(f"An error occurred while authorizing the bot with Trakt: {e}")

    @trakt.command()
    async def settraktcode(self, ctx: commands.Context, code: str):
        """Set the Trakt authorization code."""
        try:
            trakt_client = await self.get_trakt_client()
            token = trakt_client['oauth'].token_exchange(code, 'urn:ietf:wg:oauth:2.0:oob')
            await self.config.access_token.set(token["access_token"])
            await self.config.refresh_token.set(token["refresh_token"])
            await ctx.send("Trakt authorization code set successfully.")
        except Exception as e:
            await ctx.send(f"An error occurred while setting the Trakt authorization code: {e}")

    @trakt.command()
    async def scrobblestatus(self, ctx: commands.Context):
        """Get the current scrobble status."""
        try:
            trakt_client = await self.get_trakt_client()
            access_token = await self.config.access_token()
            trakt_client['oauth'].access_token(access_token)
            scrobble = trakt_client['users'].User.get_activities('me', limit=1)
            
            if scrobble:
                scrobble = scrobble[0]
                if scrobble.action == 'scrobble':
                    if scrobble.type == 'movie':
                        movie_title = scrobble.movie.title
                        await ctx.send(f"The last scrobbled movie is: {movie_title}")
                    elif scrobble.type == 'episode':
                        show_title = scrobble.show.title
                        episode_title = scrobble.episode.title
                        await ctx.send(f"The last scrobbled episode is from the show: {show_title}, episode: {episode_title}")
                    else:
                        await ctx.send("The last scrobble is not a movie or an episode.")
                else:
                    await ctx.send("No scrobble activity found.")
            else:
                await ctx.send("No scrobble activity found.")
        except Exception as e:
            await ctx.send(f"An error occurred while retrieving the scrobble status: {e}")


def setup(bot):
    bot.add_cog(rTrakt(bot))
