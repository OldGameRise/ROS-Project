"""
Raspberry Pi GPIO module for Raspberry Pi Zero 2W
Handles GPIO initialization, control, and cleanup
"""

import time
import threading
from config import IS_RASPBERRY_PI, GPIO_CONFIG

print(f"[RaspPi] Running on Raspberry Pi: {IS_RASPBERRY_PI}")
print(f"[RaspPi] GPIO Config: {GPIO_CONFIG}")

# Try to import GPIO libraries
if IS_RASPBERRY_PI:
    try:
        import RPi.GPIO as GPIO
        GPIO_AVAILABLE = True
        print("[RaspPi] RPi.GPIO library loaded successfully")
    except ImportError as e:
        print(f"[RaspPi] Warning: RPi.GPIO not available: {e}")
        print("[RaspPi] Running in simulation mode")
        GPIO_AVAILABLE = False
        IS_RASPBERRY_PI = False
else:
    GPIO_AVAILABLE = False
    print("[RaspPi] Not on Raspberry Pi, running in simulation mode")

# GPIO state tracking
gpio_state = {
    "led_on": False,
    "blinking": False,
    "initialized": False
}

# Thread for blinking
blink_thread = None
blink_stop_event = threading.Event()

def initialize_gpio():
    """Initialize GPIO pins"""
    if not IS_RASPBERRY_PI or not GPIO_AVAILABLE:
        print("[GPIO] Simulation mode: GPIO initialized")
        gpio_state["initialized"] = True
        return True
    
    try:
        # Set pin numbering mode
        if GPIO_CONFIG["pin_mode"] == "BCM":
            GPIO.setmode(GPIO.BCM)
        else:
            GPIO.setmode(GPIO.BOARD)
        
        # Setup default LED pin
        led_pin = GPIO_CONFIG["default_led_pin"]
        GPIO.setup(led_pin, GPIO.OUT)
        GPIO.output(led_pin, GPIO.LOW)
        
        # Setup button pin if configured
        if GPIO_CONFIG["default_button_pin"]:
            button_pin = GPIO_CONFIG["default_button_pin"]
            GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        gpio_state["initialized"] = True
        print(f"[GPIO] GPIO initialized. LED on pin {led_pin}")
        return True
        
    except Exception as e:
        print(f"[GPIO] Error initializing GPIO: {e}")
        gpio_state["initialized"] = False
        return False

def toggle_led(state=None):
    """
    Toggle LED on/off
    
    Args:
        state (bool, optional): True for on, False for off. If None, toggles.
    
    Returns:
        dict: Result of operation
    """
    if not gpio_state["initialized"]:
        if not initialize_gpio():
            return {"success": False, "error": "GPIO not initialized"}
    
    # Stop blinking if active
    if gpio_state["blinking"]:
        stop_blink()
    
    # Determine new state
    if state is None:
        new_state = not gpio_state["led_on"]
    else:
        new_state = bool(state)
    
    try:
        if IS_RASPBERRY_PI and GPIO_AVAILABLE:
            led_pin = GPIO_CONFIG["default_led_pin"]
            GPIO.output(led_pin, GPIO.HIGH if new_state else GPIO.LOW)
            gpio_state["led_on"] = new_state
            
            status = "ON" if new_state else "OFF"
            print(f"[GPIO] LED turned {status} (pin {led_pin})")
        else:
            # Simulation mode
            gpio_state["led_on"] = new_state
            status = "ON" if new_state else "OFF"
            print(f"[GPIO Simulation] LED turned {status}")
        
        return {
            "success": True,
            "led_on": gpio_state["led_on"],
            "message": f"LED is now {status}"
        }
        
    except Exception as e:
        print(f"[GPIO] Error toggling LED: {e}")
        return {"success": False, "error": str(e)}

def _blink_worker(duration=5, speed=0.5):
    """Worker function for blinking LED in background"""
    if not IS_RASPBERRY_PI or not GPIO_AVAILABLE:
        # Simulation blinking
        end_time = time.time() + duration
        while not blink_stop_event.is_set() and time.time() < end_time:
            gpio_state["led_on"] = not gpio_state["led_on"]
            status = "ON" if gpio_state["led_on"] else "OFF"
            print(f"[GPIO Simulation] LED blinking: {status}")
            time.sleep(speed)
        return
    
    # Real GPIO blinking
    led_pin = GPIO_CONFIG["default_led_pin"]
    end_time = time.time() + duration
    
    try:
        while not blink_stop_event.is_set() and time.time() < end_time:
            GPIO.output(led_pin, GPIO.HIGH)
            time.sleep(speed / 2)
            if blink_stop_event.is_set():
                break
            GPIO.output(led_pin, GPIO.LOW)
            time.sleep(speed / 2)
        
        # Ensure LED is off after blinking
        GPIO.output(led_pin, GPIO.LOW)
        gpio_state["led_on"] = False
        
    except Exception as e:
        print(f"[GPIO] Error during blinking: {e}")

def blink_led(duration=5, speed=0.5):
    """
    Blink LED for specified duration
    
    Args:
        duration (float): Blinking duration in seconds
        speed (float): Blink speed in seconds (full cycle)
    
    Returns:
        dict: Result of operation
    """
    global blink_thread, blink_stop_event
    
    if not gpio_state["initialized"]:
        if not initialize_gpio():
            return {"success": False, "error": "GPIO not initialized"}
    
    # Stop any existing blinking
    if gpio_state["blinking"]:
        stop_blink()
    
    # Create new blinking thread
    blink_stop_event.clear()
    blink_thread = threading.Thread(
        target=_blink_worker,
        args=(duration, speed),
        daemon=True
    )
    
    gpio_state["blinking"] = True
    blink_thread.start()
    
    print(f"[GPIO] Started blinking for {duration} seconds at {speed}s interval")
    
    return {
        "success": True,
        "blinking": True,
        "duration": duration,
        "speed": speed,
        "message": f"Blinking LED for {duration} seconds"
    }

def stop_blink():
    """Stop blinking LED"""
    global blink_thread
    
    if gpio_state["blinking"]:
        blink_stop_event.set()
        if blink_thread and blink_thread.is_alive():
            blink_thread.join(timeout=1.0)
        
        gpio_state["blinking"] = False
        print("[GPIO] Blinking stopped")
        
        # Turn off LED
        if IS_RASPBERRY_PI and GPIO_AVAILABLE and gpio_state["initialized"]:
            try:
                led_pin = GPIO_CONFIG["default_led_pin"]
                GPIO.output(led_pin, GPIO.LOW)
                gpio_state["led_on"] = False
            except:
                pass
    
    return {"success": True, "blinking": False}

def read_button():
    """Read button state if configured"""
    if not IS_RASPBERRY_PI or not GPIO_AVAILABLE:
        return {"success": False, "error": "Simulation mode"}
    
    if not GPIO_CONFIG["default_button_pin"]:
        return {"success": False, "error": "Button not configured"}
    
    try:
        button_pin = GPIO_CONFIG["default_button_pin"]
        state = GPIO.input(button_pin)
        return {
            "success": True,
            "pressed": state == GPIO.LOW,  # Assuming pull-up, LOW when pressed
            "raw_state": state
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_gpio_status():
    """Get current GPIO status"""
    return {
        "initialized": gpio_state["initialized"],
        "led_on": gpio_state["led_on"],
        "blinking": gpio_state["blinking"],
        "is_raspberry_pi": IS_RASPBERRY_PI,
        "gpio_available": GPIO_AVAILABLE
    }

def cleanup_gpio():
    """Cleanup GPIO resources"""
    print("[GPIO] Cleaning up GPIO...")
    
    # Stop blinking
    stop_blink()
    
    # Cleanup GPIO if initialized
    if IS_RASPBERRY_PI and GPIO_AVAILABLE and gpio_state["initialized"]:
        try:
            GPIO.cleanup()
            print("[GPIO] GPIO cleanup complete")
        except Exception as e:
            print(f"[GPIO] Error during cleanup: {e}")
    
    gpio_state["initialized"] = False
    print("[GPIO] Cleanup finished")