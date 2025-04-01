import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message

# Telegram Bot Authentication using environment variables
API_ID = os.getenv("API_ID")  # Set your API ID in Heroku config
API_HASH = os.getenv("API_HASH")  # Set your API Hash in Heroku config
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set your Bot Token in Heroku config

# Initialize bot
app = Client(
    "yt_downloader_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Ensure the audio and video folders exist
os.makedirs("audio_folder", exist_ok=True)
os.makedirs("video_folder", exist_ok=True)

# YouTube download options
audio_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'audio_folder/%(title)s.%(ext)s',
}

video_opts = {
    'format': 'bestvideo/best',
    'outtmpl': 'video_folder/%(title)s.%(ext)s',
}

# 🔹 /audio command
@app.on_message(filters.command("audio"))
async def download_audio(client, message: Message):
    if len(message.command) < 2:
        await message.reply("⚠️ Please provide a YouTube URL like: `/audio <URL>`")
        return

    url = message.command[1]
    user_id = message.from_user.id  # Get user ID for DM

    try:
        await message.reply("🎵 Downloading audio... Please wait.")
        
        # Download the audio and save to a temporary file
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get("title", "Unknown title")
            ext = info_dict.get("ext", "mp3")
        
        file_path = os.path.join('audio_folder', f"{title}.{ext}")

        # Send file to user's DM
        with open(file_path, 'rb') as audio_file:
            await client.send_audio(user_id, audio_file, caption=f"✅ Here is your audio: {title}")
        
        # Delete the file after sending
        os.remove(file_path)
    except Exception as e:
        await message.reply(f"❌ Error during audio download: {str(e)}")

# 🔹 /video comm
@app.on_message(filters.command("video"))
async def download_video(client, message: Message):
    if len(message.command) < 2:
        await message.reply("⚠️ Please provide a YouTube URL like: `/video <URL>`")
        return

    url = message.command[1]
    user_id = message.from_user.id  # Get user ID for DM

    try:
        await message.reply("📹 Downloading video... Please wait.")
        
        # Download the video and save to a temporary file
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get("title", "Unknown title")
            ext = info_dict.get("ext", "mp4")
        
        file_path = os.path.join('video_folder', f"{title}.{ext}")

        # Send file to user's DM
        with open(file_path, 'rb') as video_file:
            await client.send_video(user_id, video_file, caption=f"✅ Here is your video: {title}")
        
        # Delete the file after sending
        os.remove(file_path)
    except Exception as e:
        await message.reply(f"❌ Error during video download: {str(e)}")

print("start")
