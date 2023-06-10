import discord
from redbot.core import Config, commands
import webbrowser
import aiohttp

TRAKT_AUTH_URL = "https://trakt.tv/oauth/authorize"

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
        }
        self.config.register_global(**default_config)

    async def send_error_message(self, error_message):
        channel_id = await self.config.channel_id()
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(error_message)

    async def get_session(self):
        if not hasattr(self.bot, "session") or self.bot.session.closed:
            self.bot.session = aiohttp.ClientSession()
        return self.bot.session

    @commands.Cog.listener()
    async def on_ready(self):
        client_id = await self.config.client_id()
        if not client_id:
            error_message = "Trakt client ID has not been set. Please use the set_trakt_secrets command to set it."
            await self.send_error_message(error_message)

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

    @commands.command()
    @commands.is_owner()
    async def authorize_trakt(self, ctx):
        client_id = await self.config.client_id()
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        auth_url = f"{TRAKT_AUTH_URL}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
        await ctx.send(f"Please authorize the bot by visiting the following URL and entering the provided code:\n{auth_url}")

        await self.config.access_token.set("")
        await self.config.refresh_token.set("")

    @commands.command()
    @commands.is_owner()
    async def set_trakt_code(self, ctx, code: str):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

        auth_url = f"{TRAKT_AUTH_URL}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"

        if code == "":
            await ctx.send(f"Please visit the following URL to authorize the bot and provide the authorization code:\n{auth_url}")
        else:
            headers = {
                "Content-Type": "application/json",
            }
            data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
            session = await self.get_session()
            response = await session.post(TRAKT_AUTH_URL, headers=headers, data=data)
            auth_data = await response.text()

            if response.status == 200:
                access_token = auth_data.split("&")[0].split("=")[1]
                refresh_token = auth_data.split("&")[1].split("=")[1]

                await self.config.access_token.set(access_token)
                await self.config.refresh_token.set(refresh_token)

                await ctx.send("Trakt authorization successful. You can now start monitoring Trakt activity.")
            else:
                error_message = f"An error occurred during Trakt authorization: {auth_data}"
                await ctx.send(error_message)

def setup(bot):
    cog = rTrakt(bot)
    bot.add_cog(cog)
