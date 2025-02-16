
import openai
import pyttsx3
import speech_recognition as sr
import pyaudio
import threading
import time
import cv2  # OpenCV for video plyback
import screeninfo  # To get screen resolution
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

# Global variable to keep track of whether to continue running
running = True
listening_event = threading.Event()

chatStr = ""

def chat(query):
    global chatStr
    openai.api_key = api_key  # Replace with your actual OpenAI API key
    chatStr += f"User: {query}\nAssistant: "
    
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=chatStr,
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        ai_response = response["choices"][0]["text"]
        say(ai_response)
        chatStr += f"{ai_response}\n"
        return ai_response
    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        return "Sorry, something went wrong. Please try again."
    finally:
        listening_event.clear()  # Resume video playback after generating the response

def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        
        try:
            print("Listening")
            listening_event.set()  # Pause video playback before starting to listen
            say("Listening")
            audio = r.listen(source, timeout=3)  # Reduced the timeout value to 3 seconds
            queries = r.recognize_google(audio, language="en").split(".")
            for query in queries:
                print(f"You said: {query.strip()}")
            return queries
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
            return ["Sorry, I couldn't understand that. Please try again."]
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ["Some error occurred. Please try again."]
        except sr.WaitTimeoutError as e:
            print(f"Timeout while listening; {e}")
            return ["Some error occurred. Please try again."]
        finally:
            listening_event.clear()  # Resume video playback after listening

def mainfunc():
    global running
    while running:
        queries = takeCommand()
        for query in queries:
            if query.strip():
                if query.strip().lower() in ["quit", "exit", "stop", "shutdown", "bye", "ok bye", "thank you", "ok quit", "ok exit", "ok stop", "ok shutdown", "see you again bye","ok jarvis bye","jarvis bye","bye jarvis","stop jarvis","thank you jarvis bye","see you again","jarvis see you again bye"]:
                    print("Exiting...")
                    say("Thank You...Shutting down. Good bye!")
                    running = False
                    return
                elif query.strip().lower() in[ "what is your name","tell me your name","what is name","your name please","name please","name yourself","what name","is your name","who are you","hu r u"]:
                    print("My Name is Jarvis. I am an A I assistant created by Team IPR 19. How can i assist you.")
                    say("My Name is Jarvis. I am an A I assistant created by Team IPR 19. How can i assist you.")
                elif query.strip().lower() in[ "Hi jarvis","hello jarvis"]:
                    print("Hi there, How can i help you")
                    say("Hi there, How can i help you")
                else:
                    ai_response = chat(query.strip())
                    print(f"Assistant: {ai_response}")

def play_video(video_path):
    global running

    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    # Get screen resolution
    screen = screeninfo.get_monitors()[0]
    screen_width, screen_height = screen.width, screen.height

    cv2.namedWindow('Video', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while running:
        if not cap.isOpened():
            cap = cv2.VideoCapture(video_path)
        while running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart the video
                continue
            
            if listening_event.is_set():
                time.sleep(0.1)  # Pause briefly if listening
                continue
            
            frame = cv2.resize(frame, (screen_width, screen_height))
            cv2.imshow('Video', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                running = False
                break
        cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':

    print('Welcome to Your Personal AI Assistant!')
    say("Your Personal AI Assistant is ready. How may I help you?")
    # Start the assistant function in a separate thread
    assistant_thread = threading.Thread(target=mainfunc)
    assistant_thread.start()

    # Play the video file in the main thread (or another separate thread if needed)
    video_path = "C:\\Users\\moham\\OneDrive\\Desktop\\AI assistant\\HologramWithSpeechSynthesis\\hologram.mp4"  # Replace with the actual video file path
    play_video(video_path)


    # Wait for the assistant thread to finish before exiting
    assistant_thread.join()
    print("AI Assistant has been shut down.")
