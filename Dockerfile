# Use official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Heroku uses
EXPOSE 5000

# Command to run your application
CMD ["python", "EsproAudio.py"]
