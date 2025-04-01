import os
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls, AudioStream
from pytgcalls.types import GroupCallParticipant
from pymongo import MongoClient

# Telegram API and bot credentials (these should be set as environment variables or hardcoded)
API_ID = os.getenv("API_ID")  # Your API ID
API_HASH = os.getenv("API_HASH")  # Your API HASH
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Your Bot Token
USERBOT_SESSION = os.getenv("USERBOT_SESSION")  # Your userbot session string
MONGO_URI = os.getenv("MONGO_URI")  # MongoDB URI (for storing user data)
LOGGER_ID = os.getenv("LOGGER_ID")  # Log channel/user for errors

# Initialize the client (bot) and userbot
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("userbot", session_string=USERBOT_SESSION)
vc = PyTgCalls(userbot)

# MongoDB connection to store user and song data
client = MongoClient(MONGO_URI)
db = client["music_bot"]
users_collection = db["users"]
songs_collection = db["songs"]

# Function to register new users
@app.on_message(filters.private & filters.command("start"))
def register_user(client, message):
    user_id = message.from_user.id
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id})

# Start command
@app.on_message(filters.command("start"))
def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [InlineKeyboardButton("ℹ Help", callback_data="help")]
    ])
    message.reply_text(
        "🎵 **Welcome to Telegram Music Bot!**\n\nAdd me to your group to play music in voice chat!",
        reply_markup=keyboard
    )

# Help command
@app.on_callback_query(filters.regex("help"))
def help_callback(client, callback_query):
    callback_query.message.edit_text(
        "**Music Bot Commands:**\n\n"
        "/play [song name] - Download and play a song\n"
        "/stop - Stop the music\n"
        "/broadcast [message] - Send a message to all users\n"
        "/help - Show this message",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="start")]
        ])
    )

@app.on_callback_query(filters.regex("start"))
def start_callback(client, callback_query):
    start(client, callback_query.message)

# Play command to search and play songs
@app.on_message(filters.command("play"))
def play(client, message):
    chat_id = message.chat.id
    query = " ".join(message.command[1:])

    if not query:
        message.reply_text("Please provide a song name. Example: /play Tum Hi Ho")
        return

    message.reply_text(f"🔎 Searching for '{query}'...")

    # Download the audio using yt-dlp
    song_data = download_audio(query)
    
    if not song_data:
        message.reply_text("❌ Could not download the song. Please try again.")
        return

    # Create a custom message with song details
    title = song_data["title"]
    duration = song_data["duration"]
    requested_by = message.from_user.first_name
    thumbnail = song_data["thumbnail"]

    custom_message = f"""
    ➲ **Started Streaming**

    ‣ **Title** : {title}
    ‣ **Duration** : {duration} seconds
    ‣ **Requested by** : {requested_by}
    """

    # Send the message with the song's thumbnail
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{client.me.username}?startgroup=true")]
    ])

    app.send_photo(
        chat_id=chat_id,
        photo=thumbnail,
        caption=custom_message,
        reply_markup=keyboard
    )

    message.reply_text("✅ Song downloaded, now playing!")

    # Play the song in the voice chat
    song_path = song_data['file_path']
    vc.join_group_call(chat_id, AudioStream(song_path))  # Use AudioStream for voice chat

# Function to download the audio using yt-dlp
def download_audio(query):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',  # Best audio quality
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # Output directory for audio files
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio...")
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            file_path = f"downloads/{info['title']}.mp3"

            # Save song details to MongoDB
            song_data = {
                "title": info['title'],
                "url": info['webpage_url'],
                "file_path": file_path,
                "duration": info['duration'],  # Song duration
                "thumbnail": info['thumbnail']  # Thumbnail URL
            }
            songs_collection.insert_one(song_data)
            print("Download complete!")
            return song_data
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

# Stop command to leave the voice chat
@app.on_message(filters.command("stop"))
def stop(client, message):
    chat_id = message.chat.id
    vc.leave_group_call(chat_id)
    message.reply_text("🛑 Music stopped and left the voice chat.")

# Start the bot and userbot
app.start()
userbot.start()
vc.start()
print("🎵 Music bot is now running!")
asyncio.get_event_loop().run_forever()
