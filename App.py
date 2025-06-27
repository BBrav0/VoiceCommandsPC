import speech_recognition as sr
import os
import subprocess
import pyttsx3
import google.generativeai as genai
from dotenv import load_dotenv
import keyboard  # For listening to keyboard events

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Set up voice
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


# Set speech rate
rate = engine.getProperty('rate')
engine.setProperty('rate', rate * 1.2)

# ---------------------------------------------------------------------------
# Global escape-key listener
# Pressing the ESC key anywhere while this script is running will immediately
# terminate the program with exit code 0.
# ---------------------------------------------------------------------------

keyboard.on_press_key("esc", lambda _: os._exit(0))  # use os._exit to ensure the entire process exits from the callback

# Initialize AI model
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    print(f"Error initializing AI model: {e}")
    exit(1)

def speak(text):
    """
    Converts text to speech
    """
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in speech synthesis: {e}")

def do_ai_stuff(input_text):
    print("Heard: ", input_text)
    
    # First check if it's a direct command
    if check_commands(input_text.lower()):
        return  # Exit if a command was executed
    
    # If no direct command, ask AI to interpret
    try:
        response = model.generate_content(
            f"You are a voice assistant for a pc. If the command is about 'sleep', 'shutdown', or 'restart', "
            f"return ONLY the command word (sleep/shutdown/restart). Otherwise, give a regular response. "
            f"User request: {input_text}"
        )
        
        # Check if AI returned a command
        if check_commands(response.text.lower().strip()):
            return  # Exit if AI identified a command
        else:
            # If not a command, speak the AI's response
            speak(response.text)
    except Exception as e:
        speak(f"Sorry, I encountered an error while processing your request: {str(e)}")
    exit(0)

def check_commands(inp):
    match inp.lower().strip():
        case "stop":
            exit(0);
        case "shutdown":
            speak("Shutting down...")
            os.system("shutdown /s /t 1")
            exit(0)
        case "restart":
            speak("Restarting...")
            os.system("shutdown /r /t 1")
            exit(0)
        case "sleep":
            speak("Turning off the monitors...")
            os.system('start /min cmd /c "timeout /t 4 & nircmd monitor off"')
            exit(0)
        case _:
            return False  # No command matched
    return True  # Command was matched and executed

def listen_for_command():
    """
    Activates the microphone, listens for a command, and processes it.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        speak("How can I help you Ben?")
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening for command...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            recognized_text = r.recognize_google(audio)
            do_ai_stuff(recognized_text)
            exit(0)

        except sr.WaitTimeoutError:
            speak("Listening timed out.")
            exit(0)
        except sr.UnknownValueError:
            speak("Sorry, I couldn't hear you.")
            exit(0)
        except sr.RequestError as e:
            speak(f"Could not request results from Google Speech Recognition service; {e}")
            exit(0)

if __name__ == "__main__":
    listen_for_command()