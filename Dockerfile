FROM python:3.12-slim

# Install system dependencies (ffmpeg and aria2c)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    aria2c \
    && rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with UID 1000 to comply with Hugging Face Spaces security
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy requirements and install python packages
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the rest of the application
COPY --chown=user . .

# Create the downloads directory
RUN mkdir -p downloads

# Expose port 7860 (required by Hugging Face Spaces)
EXPOSE 7860

# Run using gunicorn for production, bound to port 7860
CMD ["gunicorn", "--workers", "2", "--threads", "4", "--bind", "0.0.0.0:7860", "app:app"]
