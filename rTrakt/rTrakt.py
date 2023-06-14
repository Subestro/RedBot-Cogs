from redbot.core import commands
from redbot.core.bot import Red
from discord import TextChannel

class rTrakt(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(YOUR_GUILD_ID)  # Replace YOUR_GUILD_ID with the actual guild ID
        channel = discord.utils.get(guild.text_channels, name="general")  # Replace "general" with the actual channel name
        await channel.send("rTrakt cog loaded!")

def setup(bot: Red):
    bot.add_cog(rTrakt(bot))
