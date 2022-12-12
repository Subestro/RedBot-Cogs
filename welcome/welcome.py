import json
from discord.ext.commands import Cog
import discord
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
from redbot.core.bot import Red
from redbot.core import commands
from inflect import engine

class welcome(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.welcome_channel = None

            # Load the welcome channel from the JSON file
        try:
            with open("welcome_channel.json", "r") as f:
                data = json.load(f)
                channel_id = data["welcome_channel"]
                self.welcome_channel = self.bot.get_channel(channel_id)
        except (FileNotFoundError, KeyError):
            pass

        # set the channel for the welcome message and update the JSON file
    @commands.command()
    async def setchannel(self, ctx, channel: discord.TextChannel):
        """Sets the channel where the bot will send the welcome message."""
        self.welcome_channel = channel
        await ctx.send(f"Welcome channel set to {channel.mention}.")

        # Save the welcome channel to the JSON file
        with open("welcome_channel.json", "w") as f:
             data = {"welcome_channel": self.welcome_channel.id}
             json.dump(data, f)

        # unset the channel for the welcome message and update the JSON file
    @commands.command()
    async def unsetchannel(self, ctx):
        """Unsets the channel where the bot will send the welcome message."""
        self.welcome_channel = None
        await ctx.send("Welcome channel unset.")

        # Save the updated welcome channel to the JSON file after it has been unset
        with open("welcome_channel.json", "w") as f:
             data = {"welcome_channel": self.welcome_channel}
             json.dump(data, f)

    @Cog.listener()
    async def on_red_event(self):
        # Get the server owner
        guild_id = self.bot.guilds[0].id
        server_owner = self.bot.get_guild(guild_id).owner

        # Check if the server owner is None (account may have been deleted)
        if server_owner is not None:
            # Check if the welcome channel is set
            if self.welcome_channel is None:
                # Get the server name
                server_name = self.bot.get_guild(guild_id).name

                # Send the reminder message to the server owner
                await server_owner.send(f"The welcome channel to announce new users who have joined the server has not been set. Please set the welcome channel for the {server_name} server using the `!setchannel` command.")

            # Get a dictionary of all loaded cogs and their corresponding cog classes
            loaded_cogs = self.bot.cogs

            # Create a list of the names of the loaded cogs
            loaded_cog_names = [cog_class.__class__.__name__ for cog_class in loaded_cogs.values()]

            # Send a list of the loaded cogs to the server owner
            await server_owner.send(f"The following cogs are loaded: {', '.join(loaded_cog_names)}")

    @Cog.listener()
    async def on_member_join(self, member):
        # Define the server_owner variable and set its initial value to None
        server_owner = None
        # Create an instance of the engine class
        inflector = engine()
        # Check if the welcome channel is set
        if self.welcome_channel is None:

            # Get the server name
            server_name = member.guild.name

            # Get the server owner
            server_owner = member.guild.owner

        # Check if the server owner is None (account may have been deleted)
        if server_owner is not None:
            await server_owner.send(f"The welcome channel to announce new users who have joined the server has not been set. Please set the welcome channel for the {server_name} server using the `!setchannel` command.")
            return

        # Send the welcome message to the specified channel
        channel = self.welcome_channel
        await channel.send(f"Welcome to the server, {member.mention}!")

        # Download the user's profile picture and the welcome image
        profile_picture_url = str(member.avatar_url_as(format="png"))
        welcome_image_url = "https://raw.githubusercontent.com/Subestro/RedBot-Cogs/main/welcome/img/welcome.png"
        profile_picture = Image.open(BytesIO(requests.get(profile_picture_url).content))
        welcome_image = Image.open(BytesIO(requests.get(welcome_image_url).content))

        # Make the profile picture a round image and add it to the welcome image
        size = (226, 226)
        profile_picture = ImageOps.fit(profile_picture, size, Image.ANTIALIAS)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        profile_picture.putalpha(mask)
        welcome_image_width, welcome_image_height = welcome_image.size
        profile_picture_offset = ((welcome_image_width - size[0]) // 2, (welcome_image_height - size[1]) // 2 - 60)
        welcome_image.paste(profile_picture, profile_picture_offset, profile_picture)

        # Add the text "WELCOME!" to the welcome image
        font_url = "https://raw.githubusercontent.com/Subestro/RedBot-Cogs/main/welcome/font/Gotham-Black.otf"
        font = ImageFont.truetype(BytesIO(requests.get(font_url).content), size=100)
        draw = ImageDraw.Draw(welcome_image)
        welcome_text = "WELCOME!"
        text_width, text_height = draw.textsize(welcome_text, font=font)
        text_position = ((welcome_image_width - text_width) // 2, (welcome_image_height - text_height) // 2 + 90)
        draw.text(text_position, welcome_text, fill=(255, 255, 255), font=font)

        # Add the member count to the welcome image
        font = ImageFont.truetype(BytesIO(requests.get(font_url).content), size=42)
        member_count = len(member.guild.members)
        member_count_text = f"You are the \_{inflector.ordinal(member_count)}\_ user"
        text_width, text_height = draw.textsize(member_count_text, font=font)
        #text_position = ((welcome_image_width - text_width) // 2, text_position[1] + text_height)
        text_position = ((welcome_image_width - text_width) // 2, welcome_image_height - text_height - 70)
        draw.text(text_position, member_count_text, fill=(255, 255, 255), font=font)

        # Attach the updated welcome image to the message
        file = BytesIO()
        welcome_image.save(file, format="png")
        file.seek(0)
        message = await channel.send(file=discord.File(file, "welcome.png"))
