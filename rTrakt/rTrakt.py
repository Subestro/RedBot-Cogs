from discord.ext import commands
from redbot.core import Config
from urllib.parse import urlencode

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2344567891)
        default_guild = {
            "trakt_client_id": "",
            "trakt_client_secret": "",
            "trakt_redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "trakt_access_token": ""
        }
        self.config.register_guild(**default_guild)

    @commands.command()
    async def traktlogin(self, ctx):
        client_id = await self.config.guild(ctx.guild).trakt_client_id()
        redirect_uri = await self.config.guild(ctx.guild).trakt_redirect_uri()

        oauth_params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": "random_state_string",
        }
        oauth_url = f"https://trakt.tv/oauth/authorize?{urlencode(oauth_params)}"

        await ctx.send(f"Click the following link to authorize Trakt:\n{oauth_url}")

    @commands.command()
    async def settrakttoken(self, ctx, access_token):
        await self.config.guild(ctx.guild).trakt_access_token.set(access_token)
        await ctx.send("Trakt access token set successfully!")

def setup(bot):
    bot.add_cog(rTrakt(bot))
