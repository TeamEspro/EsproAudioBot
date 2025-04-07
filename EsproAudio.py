import os
import logging
from googleapiclient.discovery import build
from pyrogram import Client, filters
import yt_dlp

# Logging
logging.basicConfig(level=logging.INFO)

# Config from Heroku ENV
BOT_TOKEN = os.environ.get("7849899179:AAHEcwuDdrdaORjl1WW02wOWkKsGgrBj2mo")
API_ID = int(os.environ.get("23664108"))
API_HASH = os.environ.get("a0f978987457c5a45450dbc6b90e69e7")
YOUTUBE_API_KEY = os.environ.get("AIzaSyB0Dd46e_EwagTplRuEIo1uAiVtVDfND3c")

# Pyrogram client
app = Client("yt_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# YouTube API client
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def search_youtube(query):
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=1
    )
    response = request.execute()
    if not response["items"]:
        return None, None
    video = response["items"][0]
    video_id = video["id"]["videoId"]
    title = video["snippet"]["title"]
    return f"https://www.youtube.com/watch?v={video_id}", title

def download_audio(url, title):
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/{title}.mp3"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Send me a YouTube search query, and I'll download the audio for you!")

@app.on_message(filters.text & ~filters.command(["start"]))
async def handle_query(client, message):
    query = message.text
    await message.reply(f"Searching YouTube for: `{query}`", quote=True)

    url, title = search_youtube(query)
    if not url:
        await message.reply("No video found.")
        return

    await message.reply(f"Downloading: `{title}`")

    try:
        file_path = download_audio(url, title)
        await message.reply_audio(audio=file_path, title=title)
        os.remove(file_path)
    except Exception as e:
        await message.reply(f"Failed to download: {e}")
print("start")
app.run()
