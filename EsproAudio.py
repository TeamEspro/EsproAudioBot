import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message

# Telegram Bot Authentication (Replace with your credentials)
API_ID = 12380656  # 🔹 Replace with your API ID
API_HASH = "d927c13beaaf5110f25c505b7c071273"  # 🔹 Replace with your API Hash
BOT_TOKEN = "7795461893:AAEUuZbDO_FI3cJVWGYSdX8PKpelbA2pclM"  # 🔹 Replace with your Bot Token

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
        
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])
        
        # Get the latest downloaded file
        file_path = os.path.join('audio_folder', os.listdir('audio_folder')[-1])

        # Send file to user's DM
        await client.send_audio(user_id, file_path, caption="✅ Here is your audio!")

        # Delete the file after sending
        os.remove(file_path)
    except Exception as e:
        await message.reply(f"❌ Error during audio download: {str(e)}")

# 🔹 /video command
@app.on_message(filters.command("video"))
async def download_video(client, message: Message):
    if len(message.command) < 2:
        await message.reply("⚠️ Please provide a YouTube URL like: `/video <URL>`")
        return

    url = message.command[1]
    user_id = message.from_user.id  # Get user ID for DM

    try:
        await message.reply("📹 Downloading video... Please wait.")
        
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])
        
        # Get the latest downloaded file
        file_path = os.path.join('video_folder', os.listdir('video_folder')[-1])

        # Send file to user's DM
        await client.send_video(user_id, file_path, caption="✅ Here is your video!")

        # Delete the file after sending
        os.remove(file_path)
    except Exception as e:
        await message.reply(f"❌ Error during video download: {str(e)}")

print("start")
