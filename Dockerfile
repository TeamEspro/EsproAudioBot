# Step 1: Use official Python image
FROM python:3.10

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy all project files
COPY . .

# Step 4: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Start the bot when container runs
CMD python3 -m EsproAudio
