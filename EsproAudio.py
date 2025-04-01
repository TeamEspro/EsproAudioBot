import os
import asyncio
import yt_dlp
import pymongo
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputAudioStream

# Heroku Config Vars (for environment variables)
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
USERBOT_SESSION = os.getenv("USERBOT_SESSION")
MONGO_URI = os.getenv("MONGO_URI")
LOGGER_ID = os.getenv("LOGGER_ID")
OWNER_ID = int(os.getenv("OWNER_ID"))

# Initialize bot, userbot, and database
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("userbot", session_string=USERBOT_SESSION)
vc = PyTgCalls(userbot)
client = pymongo.MongoClient(MONGO_URI)
db = client["telegram_music_bot"]
songs_collection = db["songs"]
users_collection = db["users"]

# Store user details
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

# Broadcast command
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))  # Only the owner can use this command
async def broadcast(client, message):
    text = message.text.split(" ", 1)[1] if len(message.command) > 1 else "Broadcast message."
    users = users_collection.find()
    count = 0
    for user in users:
        try:
            await client.send_message(user["user_id"], text)
            count += 1
        except Exception as e:
            print(f"Error sending message to {user['user_id']}: {e}")
    message.reply_text(f"✅ Broadcast sent to {count} users.")

# Download audio from YouTube
def download_audio(query):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',  # Best audio quality
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # Output directory for audio files
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Audio download ho raha hai...")
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            file_path = f"downloads/{info['title']}.mp3"

            # Save song details to MongoDB
            song_data = {
                "title": info['title'],
                "url": info['webpage_url'],
                "file_path": file_path,
                "duration": info['duration'],  # Store duration of song
                "thumbnail": info['thumbnail']  # Store thumbnail URL
            }
            songs_collection.insert_one(song_data)
            print("Audio download complete!")
            return song_data
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

# Play command
@app.on_message(filters.command("play"))
def play(client, message):
    chat_id = message.chat.id
    query = " ".join(message.command[1:])

    if not query:
        message.reply_text("कृपया गाने का नाम दें। उदाहरण: /play Tum Hi Ho")
        return

    message.reply_text(f"🔎 '{query}' खोजा जा रहा है...")
    song_data = download_audio(query)

    if not song_data:
        message.reply_text("❌ गाना डाउनलोड नहीं हो सका। कृपया फिर से प्रयास करें।")
        return

    # Create custom message with song details and thumbnail
    title = song_data["title"]
    duration = song_data["duration"]
    requested_by = message.from_user.first_name
    thumbnail = song_data["thumbnail"]

    custom_message = f"""
    ➲ **Sᴛᴀʀᴛᴇᴅ Sᴛʀᴇᴀᴍɪɴɢ**

    ‣ **Tɪᴛʟᴇ** : {title}
    ‣ **Dᴜʀᴀᴛɪᴏɴ** : {duration} seconds
    ‣ **Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ** : {requested_by}
    """

    # Send the message with song thumbnail
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{client.me.username}?startgroup=true")]
    ])

    app.send_photo(
        chat_id=chat_id,
        photo=thumbnail,
        caption=custom_message,
        reply_markup=keyboard
    )

    message.reply_text("✅ गाना डाउनलोड हो गया, अब प्ले हो रहा है!")

    # Play the audio
    song_path = song_data['file_path']
    vc.join_group_call(chat_id, InputAudioStream(song_path))

# Stop command
@app.on_message(filters.command("stop"))
def stop(client, message):
    chat_id = message.chat.id
    vc.leave_group_call(chat_id)
    message.reply_text("🛑 म्यूजिक बंद कर दिया गया है।")

# Log errors to Logger group
@app.on_error()
async def log_error(client, error):
    try:
        await client.send_message(LOGGER_ID, f"Error occurred: {error}")
    except Exception as e:
        print(f"Error logging to LOGGER_ID: {e}")

# Start bot and userbot
app.start()
userbot.start()
vc.start()
print("🎵 Telegram Music Bot चालू हो गया है!")
asyncio.get_event_loop().run_forever()
