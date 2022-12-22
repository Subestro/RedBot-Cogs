# Import the necessary libraries and modules
import requests
import json
import redbot.core

# Configure the trakt API with your client ID and client secret
trakt_client_id = "your_client_id"
trakt_client_secret = "your_client_secret"
trakt_headers = {
    "Content-Type": "application/json",
    "trakt-api-key": trakt_client_id,
    "trakt-api-version": "2"
}

@redbot.core.cog()
class rTrakt:
    def __init__(self, bot):
        self.bot = bot
    
    def update_scrobbler_status(self):
        # Retrieve your current scrobbler status from the trakt API
        scrobbler_response = requests.get("https://api.trakt.tv/sync/playback/latest", headers=trakt_headers)
        scrobbler_data = scrobbler_response.json()
        
        # Extract the show or movie title and progress from the scrobbler data
        if "show" in scrobbler_data:
            # Extract show title and progress
            show_title = scrobbler_data["show"]["title"]
            show_progress = scrobbler_data["progress"]
            scrobbler_status = f"Watching {show_title} - {show_progress}%"
        elif "movie" in scrobbler_data:
            # Extract movie title and progress
            movie_title = scrobbler_data["movie"]["title"]
            movie_progress = scrobbler_data["progress"]
            scrobbler_status = f"Watching {movie_title} - {movie_progress}%"
        else:
            scrobbler_status = "Not watching anything"
        
        # Update the bot's rich presence with the scrobbler status
        redbot.core.set_rich_presence(scrobbler_status)

def setup(bot):
    bot.add_cog(rTrakt(bot))

# Set the function to run every time you start watching something new
trakt_api.on_start_watching(rTrakt.update_scrobbler_status)
