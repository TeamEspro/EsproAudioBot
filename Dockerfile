# Use an official Python runtime as base image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (not required for Telegram bots, but useful for debugging)
EXPOSE 8080

# Set environment variables (Optional: Use Heroku config vars instead)
ENV API_ID=${API_ID}
ENV API_HASH=${API_HASH}
ENV BOT_TOKEN=${BOT_TOKEN}
ENV USERBOT_SESSION=${USERBOT_SESSION}
ENV MONGO_URI=${MONGO_URI}
ENV LOGGER_ID=${LOGGER_ID}
ENV OWNER_ID=${OWNER_ID}

# Start the bot
CMD ["python", "EsproAudio.py"]
