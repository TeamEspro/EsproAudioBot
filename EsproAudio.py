import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import InputStream, AudioPiped
from yt_dlp import YoutubeDL
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call = PyTgCalls(user)

# Download audio using yt-dlp
def download_audio(url):
    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": "downloads/song.%(ext)s",
        "quiet": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "downloads/song.webm"

@app.on_message(filters.command("play") & filters.group)
async def play(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("Gaane ka naam ya YouTube link do.")

    query = message.text.split(None, 1)[1]
    msg = await message.reply("YouTube se download ho raha hai...")

    # Download audio
    file_path = download_audio(query)

    # Join VC
    try:
        await call.join_group_call(
            message.chat.id,
            InputStream(
                AudioPiped(file_path)
            ),
            stream_type="local_stream"
        )
        await msg.edit("Gaana VC mein play ho raha hai!")
    except Exception as e:
        await msg.edit(f"Error: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop(_, message: Message):
    await call.leave_group_call(message.chat.id)
    await message.reply("Playback stop kar diya gaya.")

# Start everything
async def main():
    await app.start()
    await user.start()
    await call.start()
    print("Bot is running...")
    await idle()
    await app.stop()
    await user.stop()

if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.mkdir("downloads")
    asyncio.get_event_loop().run_until_complete(main())
