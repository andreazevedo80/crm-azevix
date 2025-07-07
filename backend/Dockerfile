FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY . .

# Make the boot script executable
RUN chmod +x /app/boot.sh

# Expose port
EXPOSE 5090

# Set the startup command to our new script
CMD ["/app/boot.sh"]