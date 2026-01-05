# ROS Project
# Raspberry Pi Zero 2W AI Assistant with GPIO Control

[![Build: Precompiled llama-cpp](https://img.shields.io/badge/Build-Precompiled_llama_for_ARM64-blue)](https://github.com/OldGameRise/ROS-Project/releases/tag/arm64-linux-2025-12-12)

A lightweight AI assistant optimized for Raspberry Pi Zero 2W that can tell time and control GPIO pins. This project uses a quantized language model (SmolLM2-360M) to process natural language commands and perform physical actions like controlling LEDs.

## Features

- **Natural Language Processing**: Uses a 360M parameter AI model for understanding commands
- **GPIO Control**: Control LEDs and read buttons through natural language
- **Time Management**: Get accurate system time (no AI hallucinations)
- **Optimized for RPi Zero 2W**: Memory-efficient configuration for limited hardware
- **Simulation Mode**: Test on regular computers without GPIO hardware
- **Automatic Cleanup**: Proper GPIO cleanup on exit

## Hardware Requirements

- Raspberry Pi Zero 2W
- MicroSD card (8GB minimum)

## Software Requirements

- Raspberry Pi OS Lite (Bullseye or Bookworm, 64-bit recommended)
- Python 3.9 or higher
- Required Python packages:
  - `llama-cpp-python` (precompiled ARM64 version provided)
  - `RPi.GPIO` (for GPIO control)

## Installation

### Quick Install (Using Precompiled Package)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/raspberry-ai-assistant.git
   cd raspberry-ai-assistant
   ```

2. **Run the installation script:**
   ```bash
   chmod +x install_rpi.sh
   ./install_rpi.sh
   ```

3. **Download the AI model:**
   The installation script will automatically download the SmolLM2-360M-Instruct-Q2_K.gguf model.

## Hardware Setup

### Basic LED Connection

Connect an LED to your Raspberry Pi Zero 2W:

```
LED Setup:
  - LED Anode (long leg) → GPIO 17 (Pin 11)
  - LED Cathode (short leg) → GND (Pin 9) via 330Ω resistor
```

### Pinout Reference

```
Raspberry Pi Zero 2W GPIO (BCM numbering):
  - GPIO 17: Physical Pin 11 (Default LED)
  - GPIO 27: Physical Pin 13 (Optional button)
  - 3.3V:    Physical Pin 1 or 17
  - GND:     Physical Pin 6, 9, 14, 20, 25, 30, 34, or 39
```

### Button Connection (Optional)

To add a button for input:
```
Button Setup:
  - Button Pin 1 → GPIO 27 (Pin 13)
  - Button Pin 2 → GND (Pin 9)
  - Enable internal pull-up resistor (configured in code)
```

## Usage

### Starting the Assistant

```bash
source ai_env/bin/activate  # If using virtual environment
python main.py
```

### Available Commands

Once running, you can use natural language commands:

**Time-related:**
- "What time is it?"
- "Tell me the current time"
- "What's the time?"

**LED Control:**
- "Turn on the LED"
- "Turn off the light"
- "Toggle the LED"
- "Blink the LED"
- "Blink for 10 seconds"
- "Stop blinking"

**System Commands:**
- "Show status"
- "Get system info"
- "quit" or "exit" to end

## Configuration

Edit `config.py` to customize:

- **GPIO Pins**: Change LED or button pins
- **Model Settings**: Adjust context size or threads
- **System Prompt**: Modify the AI's behavior
- **Blink Parameters**: Change blink duration or speed

### Using the Precompiled Package

If compilation of `llama-cpp-python` fails (common on Raspberry Pi Zero 2W), for now I have compiled llama-cpp (not llama-cpp-python) for Zero 2W in [releases](https://github.com/OldGameRise/ROS-Project/releases/tag/arm64-linux-2025-12-12). I will compile llama-cpp-python in future.

## Performance Notes

I have tested Qwen1.5-0.5B.i1-IQ1_S.gguf, the iteration speed was about 0.08it/s which is too slow for Raspberry Pi Zero 2 W to handle.

Recommended: Use SmolLM2-360M-Instruct-Q2_K.gguf which is usable speed for Raspberry Pi Zero 2 W to handle.
