import discord
from redbot.core import commands
import instagrapi
import asyncio

class rIG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_channel = None
        self.config_data = {}

    @commands.command()
    async def set_update_channel(self, ctx, channel: discord.TextChannel):
        self.update_channel = channel
        await ctx.send(f'Updates will be sent to {channel.mention}')

    def check_followers(self, user_name, password):
        api = instagrapi.Client(user_name, password)
        try:
            followers = api.followers()
            if self.config_data['followers'] != followers:
                changes = self.get_changes(self.config_data['followers'], followers)
                self.send_updates(changes)
                self.config_data['followers'] = followers
        except instagrapi.exceptions.InstagramError as e:
            print(e)

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

    async def check_followers_loop(self):
        while True:
            self.check_followers(user_name, password)
            await asyncio.sleep(3600) # check every hour

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready!')
        await self.check_followers_loop()

def setup(bot):
    bot.add_cog(rIG(bot))
