import discord
from redbot.core import commands
import trakt.core

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trakt_client = trakt.core.Client(client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET')

    @commands.command()
    async def set_watching(self, ctx):
        # Redirect the user to the Trakt authorization URL
        auth_url = self.trakt_client.auth.authorization_url('urn:ietf:wg:oauth:2.0:oob')
        await ctx.send(f'Please visit the following URL to authorize the bot to access your Trakt account: {auth_url}')

        # Wait for the user to enter the authorization code
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            return await ctx.send('Timed out waiting for authorization code.')

        # Exchange the authorization code for an access token
        code = msg.content
        access_token = self.trakt_client.auth.exchange_code_for_token(code)
        self.trakt_client.set_access_token(access_token)

        # Set the bot's rich presence to show what the user is currently watching
        currently_watching = self.trakt_client.users.watching()
        activity = discord.Game(name=currently_watching.item.title)
        await self.bot.change_presence(activity=activity)
        await ctx.send('Successfully set rich presence to show what you are currently watching.')

def setup(bot):
    bot.add_cog(rTrakt(bot))
