#!/bin/bash
# Installation script for Raspberry Pi Zero 2W

echo "Installing AI Assistant on Raspberry Pi Zero 2W..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python dependencies
sudo apt-get install python3-pip python3-venv -y

# Install GPIO library
sudo apt-get install python3-rpi.gpio -y

# Create virtual environment
python3 -m venv ai_assistant_env
source ai_assistant_env/bin/activate

# Install Python packages
pip install llama-cpp-python

# Download model (if not already present)
if [ ! -f "SmolLM2-360M-Instruct-Q2_K.gguf" ]; then
    echo "Downloading model..."
    wget https://huggingface.co/bartowski/SmolLM2-360M-Instruct-GGUF/resolve/main/SmolLM2-360M-Instruct-Q2_K.gguf
fi

echo "Installation complete!"
echo "To run: source ai_assistant_env/bin/activate && python main.py"