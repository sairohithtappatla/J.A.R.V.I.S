from wakeword.wakeword import WakeWordDetector
from tts.tts import speak  
import pygame  
import threading
import time

ACCESS_KEY = "c3HdR17LriuHTqom3X9e0xYaECgVCeLJZryNWkFcaAPfs+chifME+g=="
KEYWORD_PATH = "wakeword/jarvis.ppn"

# Initialize pygame mixer
pygame.mixer.init()

def play_sound(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)

def handle_command(command_text):
    """Handle the final transcribed command"""
    print(f"\n🤖 Processing command: {command_text}")
    speak(f"You said: {command_text}")

def on_wake():
    play_sound("sounds/bootup.mp3")
    speak("Yes sir, I'm listening...")
    print("🎙️ Speak now... Live transcription will appear below:")
    print("-" * 50)
    
    # Create real live STT instance
    
    # Start live listening in a separate thread
    def listen_for_command():
        try:
            live_stt.start_live_listening()
        except KeyboardInterrupt:
            print("\n🛑 Command listening stopped.")
        except Exception as e:
            print(f"\n❌ Listening error: {e}")
    
    # Listen for 30 seconds max, then return to wake word
    listener_thread = threading.Thread(target=listen_for_command)
    listener_thread.daemon = True
    listener_thread.start()
    
    # Wait for completion or timeout
    listener_thread.join(timeout=30)  # 30 second timeout
    
    if listener_thread.is_alive():
        print("\n⏰ Timeout reached, stopping listener...")
        live_stt.stop_listening()
    
    print("\n" + "="*50)
    print("🎙️ Returning to wake word listening...")

if __name__ == "__main__":
    print("🚀 Starting JARVIS...")
    print("Say 'Hey Jarvis' to activate...")
    detector = WakeWordDetector(
        access_key=ACCESS_KEY,
        keyword_path=KEYWORD_PATH,
        on_detect=on_wake,
        sensitivities=[0.8],  # Fixed to match single keyword
        device_index=None
    )
    detector.listen()