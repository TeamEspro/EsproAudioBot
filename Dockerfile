# Use latest Ubuntu LTS
FROM ubuntu:jammy

# Install essential dependencies
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y git libxrender1 python3-pip curl \
    && apt-get install -y ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (v16, as required for pytgcalls)
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs

# Copy application files
COPY . /app/
WORKDIR /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Start the application
CMD ["python3", "EsproAudio.py"]
