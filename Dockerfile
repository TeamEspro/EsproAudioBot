FROM ubuntu:latest

# Install required packages
RUN apt update && apt install -y python3 python3-pip ffmpeg nodejs npm && apt clean

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -U -r requirements.txt

# Start the bot
CMD ["python3", "EsproAudio.py"]
