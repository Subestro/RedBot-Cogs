import discord
from redbot.core import commands, Config, checks
from trakt import Trakt

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Use a unique identifier for your cog

        # Set the default values for the config options
        self.config.register_global(
            client_id=None,
            client_secret=None,
            channel_id=None
        )

    @commands.command()
    async def settraktchannel(self, ctx, channel: discord.TextChannel):
        await self.config.channel_id.set(channel.id)
        await ctx.send(f"Trakt messages will be sent to {channel.mention}.")

    @commands.command()
    async def settraktcredentials(self, ctx, client_id, client_secret):
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)
        await ctx.send("Trakt credentials have been set.")

    @commands.command()
    async def trakt(self, ctx):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        channel_id = await self.config.channel_id()

        if client_id is None or client_secret is None:
            await ctx.send("Please configure the Trakt API credentials first.")
            return

        if channel_id is None:
            await ctx.send("Please set the Trakt channel first using the settraktchannel command.")
            return

        Trakt.configuration.defaults.client(
            id=client_id,
            secret=client_secret,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )

        auth_url = Trakt['oauth'].authorize_url(display='page')
        await ctx.send(f"Please visit the following URL to authorize the Trakt API: {auth_url}")

        def check_authorization_message(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            auth_message = await self.bot.wait_for('message', check=check_authorization_message, timeout=120)
        except asyncio.TimeoutError:
            await ctx.send("Authorization timeout.")
            return

        auth_code = auth_message.content.strip()

        try:
            Trakt['oauth'].token(auth_code)
        except Exception as e:
            await ctx.send(f"Authorization failed. Error: {str(e)}")
            return

        movie = Trakt['search'].movie('The Matrix')[0]
        await ctx.send(f"Watching {movie.title} on {movie.year}.")

    @commands.Cog.listener()
    async def on_ready(self):
        print("rTrakt cog is ready.")

def setup(bot):
    bot.add_cog(rTrakt(bot))
