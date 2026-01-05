"""
Main entry point for the Raspberry Pi AI assistant
"""

import sys
import os
import signal
import atexit

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from init import AISystem
from action import cleanup_actions
from config import IS_RASPBERRY_PI, GPIO_CONFIG


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print(f"\n\n⚠️  Received signal {signum}. Cleaning up...")
    cleanup_actions()
    print("👋 Goodbye!")
    sys.exit(0)


def display_welcome():
    """Display welcome message and instructions"""
    print("\n" + "="*60)
    print("🤖 RASPBERRY PI ZERO 2W AI ASSISTANT".center(60))
    print("="*60)
    
    print(f"\n📋 System: {'Raspberry Pi Zero 2W ✅' if IS_RASPBERRY_PI else 'Simulation Mode 🔄'}")
    
    print("\n💡 AVAILABLE COMMANDS:")
    print("  • Time related:")
    print("    - 'What time is it?'")
    print("    - 'Tell me the current time'")
    print("    - 'Time please'")
    
    print("\n  • LED Control (GPIO):")
    print("    - 'Turn on the LED'")
    print("    - 'Turn off the light'")
    print("    - 'Toggle the LED'")
    print("    - 'Blink the LED'")
    print("    - 'Blink for 10 seconds'")
    print("    - 'Stop blinking'")
    
    print("\n  • System:")
    print("    - 'Show status'")
    print("    - 'Get system info'")
    print("    - 'quit', 'exit', or 'bye' - End program")
    
    if IS_RASPBERRY_PI:
        print(f"\n🔌 GPIO Configuration:")
        print(f"   LED Pin: GPIO{GPIO_CONFIG.get('default_led_pin', 'N/A')}")
        if GPIO_CONFIG.get('default_button_pin'):
            print(f"   Button Pin: GPIO{GPIO_CONFIG['default_button_pin']}")
    
    print("\n⚠️  Note: LED commands will control")
    print(f"   GPIO pin {GPIO_CONFIG.get('default_led_pin', 'simulated')}")
    print("="*60 + "\n")


def main():
    """Main chat loop"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Register cleanup function
    atexit.register(cleanup_actions)
    
    try:
        # Display welcome message
        display_welcome()
        
        # Initialize AI system
        print("🚀 Initializing AI Assistant...")
        ai_system = AISystem()
        
        print("\n" + "="*60)
        print("✅ Assistant is ready! Type your command below.")
        print("="*60 + "\n")
        
        # Main chat loop
        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("\n👋 Thank you for using the AI Assistant. Goodbye!")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Special commands that bypass AI
                if user_input.lower() == 'status':
                    from action import get_status_action
                    get_status_action()
                    continue
                
                # Process input through AI
                result = ai_system.process_input(user_input)
                
                # Add spacing for next input
                print()
                
            except KeyboardInterrupt:
                print("\n\n⌨️  Interrupted by user.")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("   Please try again or type 'quit' to exit.\n")
    
    except FileNotFoundError as e:
        print(f"\n❌ File Error: {str(e)}")
        print("   Please check that the model file exists in the correct location.")
        print(f"   Expected path: {os.path.abspath('./SmolLM2-360M-Instruct-Q2_K.gguf')}")
    except ImportError as e:
        print(f"\n❌ Import Error: {str(e)}")
        print("   Please install required packages:")
        print("   pip install llama-cpp-python")
        if IS_RASPBERRY_PI:
            print("   sudo apt-get install python3-rpi.gpio")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        cleanup_actions()
        print("\n" + "="*60)
        print("🤖 AI Assistant terminated.")
        print("="*60)


if __name__ == "__main__":
    main()