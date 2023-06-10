async def send_trakt_message(self, activity):
    client_id = await self.config.client_id()
    client_secret = await self.config.client_secret()
    headers = {
        "Content-Type": "application/json",
        "trakt-api-key": client_id,
        "trakt-api-version": "2",
    }
    url = f"{TRAKT_API_URL}/sync/playback"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        playback_data = response.json()
        if playback_data:
            current_item = playback_data[0]
            channel = self.bot.get_channel(YOUR_CHANNEL_ID)  # Replace with your #general channel ID
            if channel:
                message = f"Currently watching: {current_item['title']} ({current_item['year']})"
                await channel.send(message)

                # Update rich presence with the currently playing item
                await self.update_rich_presence(current_item)

def update_rich_presence(self, current_item):
    client_id = await self.config.client_id()
    client_secret = await self.config.client_secret()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {client_secret}",
    }
    data = {
        "pid": 1,  # Rich presence ID (choose any unique integer)
        "activity": {
            "details": current_item["title"],
            "timestamps": {"start": current_item["progress"]},
            "assets": {"large_image": current_item["type"]},
        },
    }
    self.bot.http.request(
        discord.http.Route("POST", f"/v8/applications/{client_id}/rich-presence/{RICH_PRESENCE_ACTIVITY_TYPE}"),
        headers=headers,
        json=data,
    )
