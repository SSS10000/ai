import eel
import threading
import speech_recognition as sr
import pyttsx3
import psutil
import shutil
import datetime
import os
import time
import subprocess

# Initialize Eel with frontend folder
eel.init(".")

# Text-to-Speech setup
engine = pyttsx3.init()
engine.setProperty("rate", 175)

def speak(text):
    print("AI:", text)
    engine.say(text)
    engine.runAndWait()

# Common function to handle command (text or voice)
def process_command(command):
    command = command.lower().strip()

    if "hello jarvis" in command:
        speak("Hello Boss")

    elif "create folder" in command:
        folder_name = command.replace("create folder", "").strip()
        if folder_name:
            try:
                os.makedirs(folder_name, exist_ok=True)
                speak(f"Folder {folder_name} created.")
            except Exception as e:
                speak(f"Could not create folder: {str(e)}")
        else:
            speak("Please provide folder name.")

    elif "delete folder" in command:
        folder_name = command.replace("delete folder", "").strip()
        if folder_name:
            try:
                shutil.rmtree(folder_name)
                speak(f"Folder {folder_name} deleted.")
            except Exception as e:
                speak(f"Could not delete folder: {str(e)}")
        else:
            speak("Please provide folder name.")

    elif "sleep pc" in command:
        speak("Putting PC to sleep.")
        os.system("systemctl suspend")

    elif "restart pc" in command:
        speak("Restarting the system.")
        os.system("reboot")

    elif "shutdown pc" in command:
        speak("Shutting down the system.")
        os.system("shutdown now")

    elif "clear trash" in command or "empty trash" in command:
        os.system("rm -rf ~/.local/share/Trash/*")
        speak("Trash cleared.")

    elif "open browser" in command:
        speak("Opening browser.")
        os.system("xdg-open https://www.google.com")

    elif "close open window" in command:
        speak("Closing all open windows.")
        os.system("xdotool search --onlyvisible --class '' windowkill")  # xdotool needed

    elif "cpu" in command:
        cpu = psutil.cpu_percent()
        speak(f"CPU usage is {cpu} percent.")

    elif "date" in command or "time" in command:
        now = datetime.datetime.now()
        speak(f"The time is {now.strftime('%Y-%m-%d %H:%M:%S')}")

    else:
        speak("Sorry, I did not understand that command.")

# Voice listener (runs in a thread)
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        eel.showTranscript("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        eel.showTranscript(f"You said: {text}")
        process_command(text)
    except sr.UnknownValueError:
        eel.showTranscript("Sorry, I didn't understand that.")
        speak("Sorry, I didn't understand that.")
    except sr.RequestError:
        eel.showTranscript("Speech recognition service not working.")
        speak("Speech recognition service is not working.")

# Triggered from frontend for mic input
@eel.expose
def start_listening_threaded():
    threading.Thread(target=listen).start()

# Triggered from frontend for text input
@eel.expose
def process_text_command(cmd):
    eel.showTranscript(f"You typed: {cmd}")
    process_command(cmd)

# System stats fetcher
def get_system_stats():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    ram_used = round(mem.used / (1024 * 1024))
    ram_total = round(mem.total / (1024 * 1024))
    disk = shutil.disk_usage('/')
    disk_used = round(disk.used / (1024 * 1024 * 1024))
    disk_total = round(disk.total / (1024 * 1024 * 1024))
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    battery = psutil.sensors_battery()
    battery_percent = int(battery.percent) if battery else "N/A"

    return {
        "cpu": cpu,
        "ram_used": ram_used,
        "ram_total": ram_total,
        "disk_used": disk_used,
        "disk_total": disk_total,
        "date_time": now,
        "battery": battery_percent
    }

# Repeatedly update frontend with system stats
def update_stats_periodically():
    while True:
        stats = get_system_stats()
        eel.updateSystemStats(stats)
        time.sleep(5)

# Start everything
if __name__ == "__main__":
    threading.Thread(target=update_stats_periodically, daemon=True).start()
    speak("Welcome Boss")
    eel.start("jarvicai.html", size=(800, 600))
