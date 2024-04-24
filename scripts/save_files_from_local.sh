#!/bin/bash

# Remote server SSH login details
read -p "Enter your SSH username: " REMOTE_USER
read -p "Enter the host IP or domain (e.g.,): " REMOTE_HOST

# Remote and local paths are fixed based on your information
REMOTE_PATH="swarms-cloud/*.gif"  # Adjust this if the exact path is different
LOCAL_DIR="$HOME/Desktop"  # Default path to the user's Desktop

# Use scp to fetch all .gif files from remote directory
echo "Attempting to download .gif files from $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH to your Desktop..."
scp "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH" "$LOCAL_DIR"

# Check if scp command was successful
if [ $? -eq 0 ]; then
    echo "Download completed. All .gif files have been saved to your Desktop at $LOCAL_DIR"
else
    echo "Download failed. Check the SSH details and remote path, and ensure your SSH keys are set up correctly."
fi
