"""
Configuration for the AI system
"""

import sys
import platform

# System detection
SYSTEM_INFO = {
    "platform": sys.platform,
    "machine": platform.machine(),
    "processor": platform.processor()
}

# Check if running on Raspberry Pi
IS_RASPBERRY_PI = SYSTEM_INFO["machine"].startswith("arm") or "raspberry" in SYSTEM_INFO["processor"].lower()

# Model configuration
MODEL_PATH = "./SmolLM2-360M-Instruct-Q2_K.gguf"
MODEL_CONFIG = {
    "n_ctx": 1024,  # Reduced for RPi Zero 2W memory constraints
    "n_threads": 4,  # Use all cores on RPi Zero 2W
    "n_gpu_layers": 0,  # CPU only for RPi
    "verbose": False,
    "use_mlock": True  # Lock memory to prevent swapping
}

# Raspberry Pi specific configuration
if IS_RASPBERRY_PI:
    # Optimize for Raspberry Pi Zero 2W
    MODEL_CONFIG.update({
        "n_batch": 128,  # Smaller batch size for RPi memory
        "n_threads_batch": 2,  # Threads for batch processing
    })
    
    # GPIO Configuration
    GPIO_CONFIG = {
        "pin_mode": "BCM",  # BCM pin numbering (GPIO numbers, not physical pins)
        "default_led_pin": 17,  # GPIO17 (physical pin 11)
        "default_button_pin": 27,  # GPIO27 (physical pin 13)
        "pwm_frequency": 100,  # Hz
    }
else:
    GPIO_CONFIG = {
        "simulation_mode": True,
        "default_led_pin": None,
        "default_button_pin": None,
    }

# System prompt configuration
SYSTEM_PROMPT = """You are an AI assistant running on a Raspberry Pi Zero 2W. You can tell the current time and control GPIO pins.

RESPONSE FORMAT RULES:
1. For ALL responses, you MUST use this EXACT JSON format:
{
  "text": "Your conversational response here",
  "action": "action_name" OR null
}

2. The "text" field should contain your normal conversational response.

3. The "action" field should ONLY contain one of these when requested:
- "print_time": when user asks about time, clock, or what time it is
- "toggle_led": when user asks to turn on/off LED, light, or toggle GPIO
- "blink_led": when user asks to blink, flash LED
- null: for all other conversations

4. ACTION EXAMPLES:
- User: "What time is it?" → {"text": "I'll check the time.", "action": "print_time"}
- User: "Turn on the LED" → {"text": "Turning on the LED.", "action": "toggle_led"}
- User: "Blink the light" → {"text": "I'll make it blink.", "action": "blink_led"}
- User: "Hello" → {"text": "Hello! I'm ready.", "action": null}

5. IMPORTANT: Never invent or guess the time. Always use "print_time" action.
6. Keep responses brief and natural.
7. Use ONLY valid JSON format. No other text."""