import discord
from redbot.core import commands, Config, checks
from trakt import Trakt, TraktDeviceAuth

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

        Trakt.configure(client_id=client_id, client_secret=client_secret)
        Trakt.authorization = TraktDeviceAuth()
        auth_url = Trakt.authorization_url()
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
            Trakt.authorization = TraktDeviceAuth()
            Trakt.authorization = Trakt.authorization_from_code(auth_code)
        except TraktException as e:
            await ctx.send(f"Authorization failed. Error: {str(e)}")
            return

        await ctx.send("Authorization successful.")

    @commands.Cog.listener()
    async def on_ready(self):
        print("rTrakt cog is ready.")

def setup(bot):
    bot.add_cog(rTrakt(bot))
