import discord
from redbot.core import commands, Config
import instagrapi
import asyncio

class rIG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_channel = None
        self.config = Config.get_conf(self, identifier=1337)
        default_global = {
            'user_name': None,
            'password': None,
            'update_channel': None,
            'followers': []
        }
        self.config.register_global(**default_global)

    @commands.command()
    async def set_update_channel(self, ctx, channel: discord.TextChannel):
        self.update_channel = channel
        await self.config.update_channel.set(channel.id)
        await ctx.send(f'Updates will be sent to {channel.mention}')

    @commands.command()
    async def set_credentials(self, ctx, user_name: str, password: str):
        await self.config.user_name.set(user_name)
        await self.config.password.set(password)
        await ctx.send('Credentials saved')

    async def check_followers(self):
        api = instagrapi.Client(await self.config.user_name(), await self.config.password())
        try:
            followers = api.followers()
            if await self.config.followers() != followers:
                changes = self.get_changes(await self.config.followers(), followers)
                self.send_updates(changes)
                await self.config.followers.set(followers)
        except instagrapi.exceptions.InstagramError as e:
            print(e)
        await asyncio.sleep(60)  # check every 60 seconds
        await self.check_followers()

    def get_changes(self, old_followers, new_followers):
        changes = {
            'unfollowed': [],
            'followed': []
        }
        for follower in old_followers:
            if follower not in new_followers:
                changes['unfollowed'].append(follower)
        for follower in new_followers:
            if follower not in old_followers:
                changes['followed'].append(follower)
        return changes

    def send_updates(self, changes):
        if self.update_channel is None:
            return
        for user in changes['unfollowed']:
            message = f'{user} unfollowed you'
            self.update_channel.send(message)
        for user in changes['followed']:
            message = f'{user} followed you'
            self.update_channel.send(message)

def setup(bot):
    bot.add_cog(rIG(bot))