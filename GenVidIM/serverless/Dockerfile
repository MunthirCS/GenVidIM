# --- Minimal Runtime Stage ---
# This image is very small and builds quickly.
# It relies on a virtual environment stored on a network volume.
FROM python:3.10-slim

# Set the working directory
WORKDIR /workspace/GenVidIM

# Copy the application code and the startup script
COPY . /workspace/GenVidIM/

# Make the startup script executable
RUN chmod +x /workspace/GenVidIM/serverless/start.sh

# Set the entrypoint to our startup script
CMD ["/workspace/GenVidIM/serverless/start.sh"]

