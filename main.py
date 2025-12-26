import subprocess
import os
import sys
import re
import RPi.GPIO as GPIO

# ---- Configuration ----
LLAMA_CPP_MAIN = os.path.expanduser("~/bin/llama-cli")
MODEL_PATH = "./SmolLM2-360M.Q2_K.gguf"  # Use base model if preferred

# Validate paths
if not os.path.isfile(LLAMA_CPP_MAIN):
    print(f"Error: llama.cpp 'main' binary not found at {LLAMA_CPP_MAIN}")
    sys.exit(1)

if not os.path.isfile(MODEL_PATH):
    print(f"Error: Model not found at {MODEL_PATH}")
    sys.exit(1)

# Set up GPIO
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setwarnings(False)  # Suppress warnings on repeated runs

def toggle_gpio(pin: int):
    """
    Toggles a GPIO pin: turns it ON for 1 second, then OFF.
    You can modify this to just turn ON/OFF persistently if needed.
    """
    try:
        GPIO.setup(pin, GPIO.OUT)
        print(f"\n[GPIO] Turning ON pin {pin}...", end="", flush=True)
        GPIO.output(pin, GPIO.HIGH)
        # Optional: keep on for 1 sec then turn off (like a pulse)
        import time
        time.sleep(1)
        GPIO.output(pin, GPIO.LOW)
        print(" and then OFF (pulse).")
    except Exception as e:
        print(f"\n[GPIO ERROR] Failed to control pin {pin}: {e}")

def parse_gpio_command(text: str):
    """
    Extracts [GPIO<number>] from the response and returns the pin number.
    Returns None if no valid command found.
    """
    match = re.search(r'\[GPIO(\d+)\]', text)
    if match:
        try:
            pin = int(match.group(1))
            # Safety: only allow reasonable GPIO pins (0-27 on Pi)
            if 0 <= pin <= 27:
                return pin
        except ValueError:
            pass
    return None

def generate_response(prompt: str, max_tokens: int = 128) -> str:
    cmd = [
        LLAMA_CPP_MAIN,
        "-m", MODEL_PATH,
        "-p", prompt,
        "-n", str(max_tokens),
        "--temp", "0.0",          # Deterministic output for GPIO tasks
        "--top-p", "0.9",
        "--repeat-penalty", "1.0",
        "-ngl", "0",
        "--no-display-prompt"
    ]

    try:
        env = os.environ.copy()
        bin_dir = os.path.expanduser("~/bin")
        env['LD_LIBRARY_PATH'] = f"{bin_dir}:{env.get('LD_LIBRARY_PATH', '')}"

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
            env=env
        )
        if result.returncode != 0:
            print(f"\n[LLM ERROR] {result.stderr}")
            return ""

        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[EXCEPTION: {e}]"

def format_prompt(user_input: str) -> str:
    """
    Embed system instructions directly in the prompt for base models.
    Since we're using a base model (no chat template), we craft a full prompt.
    """
    system_prompt = (
        "You are an AI assistant running on a Raspberry Pi. "
        "When the user asks to turn on, off, or toggle a GPIO pin or number, "
        "respond ONLY with the exact format: [GPIOX] where X is the pin number (e.g., [GPIO18]). "
        "Do not add any other text, explanation, or punctuation."
    )
    return f"{system_prompt}\n\nUser: {user_input}\nAI:"

def process_response(response: str):
    """Check for GPIO command and execute it."""
    print(response)  # Print the raw AI output
    pin = parse_gpio_command(response)
    if pin is not None:
        toggle_gpio(pin)

def main():
    print("=" * 60)
    print("Raspberry Pi GPIO AI Controller")
    print(f"Model: {MODEL_PATH}")
    print("Base model is used → prompt includes system instructions")
    print("=" * 60)
    print("Examples: 'Turn on pin 18', 'Toggle GPIO 21', 'Switch off pin 5'")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    # Handle CLI argument
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        print(f"\nUser: {user_input}")
        print("Assistant: ", end="", flush=True)
        prompt = format_prompt(user_input)
        response = generate_response(prompt)
        process_response(response)
        GPIO.cleanup()  # Optional: cleanup before exit
        return

    # Interactive mode
    try:
        while True:
            user_input = input("\nUser: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            if not user_input:
                continue

            print("Assistant: ", end="", flush=True)
            prompt = format_prompt(user_input)
            response = generate_response(prompt)
            process_response(response)

    except (KeyboardInterrupt, EOFError):
        print("\n\nShutting down...")
    finally:
        GPIO.cleanup()  # Reset GPIO pins

if __name__ == "__main__":
    main()