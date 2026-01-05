"""
Initialize and load the AI model
"""

import json
import re
import time
from llama_cpp import Llama
from config import MODEL_PATH, MODEL_CONFIG, SYSTEM_PROMPT, IS_RASPBERRY_PI
from action import validate_action, execute_action, get_status_action


class AISystem:
    """
    Main AI system class that handles model loading and response processing
    """
    
    def __init__(self):
        """Initialize the AI model"""
        print("="*60)
        print("🤖 AI Assistant for Raspberry Pi Zero 2W")
        print("="*60)
        
        if IS_RASPBERRY_PI:
            print("✅ Running on Raspberry Pi")
        else:
            print("⚠️  Running in simulation mode (not on Raspberry Pi)")
        
        self.model = None
        self.last_response = None
        self._load_model()
        print("✅ AI System initialized successfully!")
        print("="*60)
    
    def _load_model(self):
        """Load the GGUF model using llama-cpp-python"""
        try:
            print(f"📦 Loading model from: {MODEL_PATH}")
            
            # Adjust config for RPi memory constraints
            if IS_RASPBERRY_PI:
                print("⚙️  Optimizing for Raspberry Pi Zero 2W memory...")
                time.sleep(1)  # Give time to read message
            
            self.model = Llama(
                model_path=MODEL_PATH,
                **MODEL_CONFIG
            )
            
            # Warm up the model with a simple request
            self._warm_up()
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")
    
    def _warm_up(self):
        """Send a warm-up request to initialize the model"""
        try:
            warm_up_prompt = f"{SYSTEM_PROMPT}\n\nUser: Hello\nAssistant:"
            _ = self.model(
                warm_up_prompt,
                max_tokens=50,
                stop=["User:", "\n\n"],
                temperature=0.1
            )
            print("✅ Model warm-up complete")
        except Exception as e:
            print(f"⚠️  Warning: Warm-up failed - {str(e)}")
    
    def generate_response(self, user_input):
        """
        Generate a response from the AI model
        
        Args:
            user_input (str): User's input text
            
        Returns:
            dict: Contains response text and action (if any)
        """
        # Prepare the prompt
        prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_input}\nAssistant:"
        
        # Generate response with parameters optimized for RPi
        response = self.model(
            prompt,
            max_tokens=150,  # Reduced for RPi
            stop=["User:", "###"],
            echo=False,
            temperature=0.2,  # Lower temperature for more reliable JSON
            top_p=0.9,
            repeat_penalty=1.1
        )
        
        # Extract the generated text
        ai_response = response['choices'][0]['text'].strip()
        self.last_response = ai_response
        
        # Parse the response
        parsed_response = self._parse_response(ai_response)
        
        return parsed_response
    
    def _parse_response(self, ai_response):
        """
        Parse AI response to extract JSON structure
        
        Args:
            ai_response (str): Raw AI response text
            
        Returns:
            dict: Parsed response with text and action
        """
        # Try to parse as JSON
        json_data = self._extract_json(ai_response)
        
        if json_data:
            # Validate JSON structure
            if isinstance(json_data, dict) and "text" in json_data:
                return {
                    "text": json_data.get("text", ""),
                    "action": json_data.get("action"),
                    "raw_response": ai_response
                }
        
        # Fallback: Try to extract action using keywords
        return self._fallback_parse(ai_response)
    
    def _extract_json(self, text):
        """
        Extract and parse JSON from text
        
        Args:
            text (str): Text potentially containing JSON
            
        Returns:
            dict or None: Parsed JSON or None
        """
        try:
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
        except json.JSONDecodeError:
            # Try to fix common JSON issues
            try:
                # Remove any code block markers
                cleaned = text.strip()
                if cleaned.startswith('```json'):
                    cleaned = cleaned[7:]
                if cleaned.endswith('```'):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                return json.loads(cleaned)
            except:
                pass
        return None
    
    def _fallback_parse(self, text):
        """
        Fallback parsing method using keyword matching
        
        Args:
            text (str): Raw AI response
            
        Returns:
            dict: Parsed response
        """
        text_lower = text.lower()
        
        # Check for time-related keywords
        time_keywords = ["time", "clock", "what time", "current time", "hour"]
        has_time_keyword = any(keyword in text_lower for keyword in time_keywords)
        
        # Check for LED toggle keywords
        led_keywords = ["led", "light", "turn on", "turn off", "toggle", "switch"]
        has_led_keyword = any(keyword in text_lower for keyword in led_keywords)
        
        # Check for blink keywords
        blink_keywords = ["blink", "flash", "flicker"]
        has_blink_keyword = any(keyword in text_lower for keyword in blink_keywords)
        
        # Check for stop keywords
        stop_keywords = ["stop", "end", "cease"]
        has_stop_keyword = any(keyword in text_lower for keyword in stop_keywords)
        
        # Determine action based on keywords
        if has_time_keyword:
            return {
                "text": "I'll check the current time for you.",
                "action": "print_time",
                "raw_response": text
            }
        elif has_led_keyword and not has_blink_keyword:
            return {
                "text": "I'll toggle the LED for you.",
                "action": "toggle_led",
                "raw_response": text
            }
        elif has_blink_keyword:
            if has_stop_keyword:
                return {
                    "text": "Stopping the blinking LED.",
                    "action": "stop_blink",
                    "raw_response": text
                }
            else:
                return {
                    "text": "I'll make the LED blink.",
                    "action": "blink_led",
                    "raw_response": text
                }
        elif "status" in text_lower or "state" in text_lower:
            return {
                "text": "Here's the current system status.",
                "action": "get_status",
                "raw_response": text
            }
        
        # Default: no action
        return {
            "text": text,
            "action": None,
            "raw_response": text
        }
    
    def process_input(self, user_input):
        """
        Process user input and execute any requested actions
        
        Args:
            user_input (str): User's input text
            
        Returns:
            dict: Result of processing including any action execution
        """
        # Generate AI response
        response = self.generate_response(user_input)
        
        # Display AI's text response
        print(f"\n🤖 AI: {response['text']}")
        
        # Execute action if requested
        result = {
            "response": response,
            "action_executed": False,
            "action_result": None
        }
        
        if response.get("action"):
            action_name = response["action"]
            if validate_action(action_name):
                print(f"\n⚡ Executing action: {action_name}")
                action_result = execute_action(action_name)
                result["action_executed"] = True
                result["action_result"] = action_result
                
                if not action_result["success"]:
                    print(f"❌ Action failed: {action_result.get('error', 'Unknown error')}")
        
        return result