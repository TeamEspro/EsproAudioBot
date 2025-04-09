from pyrogram import Client, filters
from pyrogram.types import Message
from googleapiclient.discovery import build
import yt_dlp
import os

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

bot = Client("yt_download_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Ensure download folder exists
os.makedirs("downloads", exist_ok=True)

# YouTube search function
def search_youtube(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    req = youtube.search().list(q=query, part="snippet", type="video", maxResults=1)
    res = req.execute()
    if res["items"]:
        video_id = res["items"][0]["id"]["videoId"]
        title = res["items"][0]["snippet"]["title"]
        return f"https://www.youtube.com/watch?v={video_id}", title
    return None, None

# Download function
def download_video(url):
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")

# /start command
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply("Hi! Send `/download song name` to download audio from YouTube.", quote=True)

# /download command
@bot.on_message(filters.command("download") & filters.private)
async def download_handler(client: Client, message: Message):
    query = message.text.split(None, 1)
    if len(query) < 2:
        return await message.reply("Usage: `/download song name`", quote=True)

    await message.reply("Searching YouTube...", quote=True)
    url, title = search_youtube(query[1])
    if not url:
        return await message.reply("No video found.", quote=True)

    await message.reply(f"Downloading: **{title}**", quote=True)
    filepath = download_video(url)

    await message.reply_audio(
        audio=filepath,
        title=title,
        caption="Downloaded from YouTube",
        quote=True
    )

    os.remove(filepath)
print("Bot Start 😤 😤")
bot.run()
