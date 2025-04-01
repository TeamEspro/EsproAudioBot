# Use Ubuntu Jammy (22.04 LTS) as the base image
FROM ubuntu:jammy

# Set non-interactive mode to prevent installation prompts
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies including Python and pip
RUN apt update && apt install -y \
    python3 python3-pip ffmpeg git curl && \
    rm -rf /var/lib/apt/lists/*

# Copy all project files into the container
COPY . .

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Step 6: Start the bot when container runs
CMD python3 -m EsproAudio
