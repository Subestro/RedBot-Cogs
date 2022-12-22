import discord
import aiohttp
import asyncio
import json

class rTrakt:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.update_presence.start()

    def __unload(self):
        self.update_presence.cancel()
        asyncio.create_task(self.session.close())

    @tasks.loop(minutes=5.0)
    async def update_presence(self):
        # Replace these values with your own client ID, client secret, and redirect URI
        client_id = 'YOUR_CLIENT_ID'
        client_secret = 'YOUR_CLIENT_SECRET'
        redirect_uri = 'YOUR_REDIRECT_URI'

        # Get the authorization code
        authorize_url = f'https://api.trakt.tv/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}'
        print(f'Visit the following URL to authorize the bot: {authorize_url}')
        code = input('Enter the authorization code: ')

        # Request an access token
        token_url = 'https://api.trakt.tv/oauth/token'
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
        headers = {'Content-Type': 'application/json'}
        async with self.session.post(token_url, data=json.dumps(payload), headers=headers) as resp:
            token_response = await resp.json()
            access_token = token_response['access_token']
            refresh_token = token_response['refresh_token']
            print(f'Access token: {access_token}')
            print(f'Refresh token: {refresh_token}')

        # Get the current watch status
        playback_url = 'https://api.trakt.tv/sync/playback/current'
        headers = {'Authorization': f'Bearer {access_token}'}
        async with self.session.get(playback_url, headers=headers) as resp:
            playback_response = await resp.json()
            if playback_response['type'] == 'episode':
                # Set the rich presence for a TV show episode
                show_name = playback_response['show']['title']
                episode_name = playback_response['episode']['title']
                season_number = playback_response['episode']['season']
                episode_number = playback_response['episode']['number']
                activity_name = f'Watching {show_name} - S{season_number:02d}E{episode_number:02d}: {episode_name}'
                activity_type = discord.ActivityType.watching
            elif playback_response['type'] == 'movie':
                # Set the rich presence for a movie
                movie_name = playback_response['movie']['title']
                activity_name = f'Watching {movie_name}'
                activity_type = discord.ActivityType.watching
            else:
                # No current playback
                activity_name = None
                activity_type = None

        # Set the rich presence
        if activity_name:
            activity = discord.Activity(name=activity_name, type=activity_type)
            await self.bot.set_activity()
