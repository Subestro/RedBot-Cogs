import discord
import trakt
from redbot.core import commands
import asyncio

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trakt_client = trakt.TraktClient(client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET')

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

        # Set up a callback function for the on_playback_start event
        async def on_playback_start(data):
            currently_watching = data['current']
            activity = discord.Game(name=f"{currently_watching.title} - {currently_watching.progress:.0f}%")
            await self.bot.change_presence(activity=activity)

        # Register the callback function for the on_playback_start event
        self.trakt_client.on('playback_start', on_playback_start)

        await ctx.send('Successfully set up a live scrobbler in the bot\'s rich presence.')

def setup(bot):
    bot.add_cog(rTrakt(bot))
