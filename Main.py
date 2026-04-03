# -*- coding: utf-8 -*-
"""
Bloom AI - Main Entry Point
Voice-controlled AI Assistant with JARVIS-style interface
"""

import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set Qt platform plugin
os.environ['QT_QPA_PLATFORM'] = 'windows'

from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

from Backend.Model import FirstLayerDMM
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.ComputerControl import ExecuteComputerCommand
from Backend.Automation import Automation, OpenApp

# Try to import SpeechToText (optional)
SpeechRecognition = None
try:
    from Backend.SpeechToText import SpeechRecognition as _SpeechRecognition
    SpeechRecognition = _SpeechRecognition
    print("Voice recognition: Available")
except Exception as e:
    print(f"Voice recognition: Not available ({e})")

from dotenv import dotenv_values
from asyncio import run
from time import sleep
import json

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
env_vars.get("Assistantname", "Bloom")
Assistantname = "Bloom"

# Ensure directories exist
os.makedirs("Data", exist_ok=True)
os.makedirs("Frontend/Files", exist_ok=True)
os.makedirs("Frontend/Graphics", exist_ok=True)

# Initialize data files
def init_data_files():
    """Initialize all required data files."""
    files = {
        'Data/ChatLog.json': '[]',
        'Frontend/Files/Database.data': '',
        'Frontend/Files/Responses.data': '',
        'Frontend/Files/Status.data': 'Ready',
        'Frontend/Files/Mic.data': 'False',
        'Frontend/Files/TextInput.data': '',
    }
    for filepath, default_content in files.items():
        try:
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(default_content)
        except Exception as e:
            print(f"Error creating {filepath}: {e}")

init_data_files()

DefaultMessage = f"Hello {Username}! I am {Assistantname}, your personal AI assistant. How may I help you?"

Functions = ["open", "close", "play", "system", "content", "google search", "execute", "youtube search"]

def ShowDefaultChatIfNoChats():
    """Initialize chat with a welcome message."""
    try:
        with open(r'Data/ChatLog.json', "r", encoding="utf-8") as f:
            content = f.read().strip()
            if len(content) < 5 or not content:
                with open(TempDirectoryPath('Responses.data'), 'w', encoding="utf-8") as file:
                    file.write(DefaultMessage)
    except Exception:
        try:
            with open(r'Data/ChatLog.json', 'w', encoding="utf-8") as f:
                json.dump([], f)
            with open(TempDirectoryPath('Responses.data'), 'w', encoding="utf-8") as file:
                file.write(DefaultMessage)
        except Exception as e:
            print(f"Error initializing chat: {e}")

def ReadChatLogJson():
    """Read the chat log from JSON file."""
    try:
        with open(r"Data/ChatLog.json", "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
            return []
    except Exception:
        return []

def SaveToChatLog(role: str, content: str):
    """Save a message to the chat log."""
    if not content:
        return
    try:
        messages = ReadChatLogJson()
        messages.append({"role": role, "content": content})
        with open(r'Data/ChatLog.json', 'w', encoding="utf-8") as f:
            json.dump(messages[-50:], f, indent=4)
    except Exception as e:
        print(f"Error saving to chat log: {e}")

def InitialExecution():
    """Run initial setup tasks."""
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    SetAssistantStatus("Ready")
    print(f"\n{'='*50}")
    print(f">> {Assistantname} AI - Voice Assistant Ready")
    print(f"{'='*50}")
    print(f"User: {Username}")
    print(f"Type your command and press Enter")
    print(f"{'='*50}\n")

InitialExecution()

def handle_input():
    """Get user input from text file."""
    try:
        text_input_file = os.path.join("Frontend/Files", "TextInput.data")
        if os.path.exists(text_input_file):
            with open(text_input_file, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            if text:
                os.remove(text_input_file)
                return text
    except:
        pass
    return None

def MainExecution(Query=None):
    """Main execution logic for processing user commands."""
    # Check for text input if not provided
    if Query is None:
        Query = handle_input()
    
    if not Query or not Query.strip():
        return False
        
    Query = Query.strip()
    ShowTextToScreen(f"{Username}: {Query}")
    SaveToChatLog("user", Query)
    print(f"\nUser: {Query}")
        
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)
    print(f"Decision: {Decision}")
    
    TaskExecution = False
    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    Merged_query = " and ".join([" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")])

    # Handle execute commands
    for queries in Decision:
        if not TaskExecution and any(queries.startswith(func) for func in Functions):
            if queries.startswith("execute "):
                command_text = queries.removeprefix("execute ").strip()
                SetAssistantStatus("Executing...")
                print(f"Executing: {command_text}")
                result = ExecuteComputerCommand(command_text)
                ShowTextToScreen(f"{Assistantname}: {result}")
                SaveToChatLog("assistant", result)
                SetAssistantStatus("Speaking...")
                try:
                    TextToSpeech(result)
                except:
                    pass
                TaskExecution = True
            else:
                SetAssistantStatus("Processing...")
                try:
                    run(Automation(list(Decision)))
                except Exception as e:
                    print(f"Automation error: {e}")
                TaskExecution = True

    # Handle general queries
    if not TaskExecution:
        if G and R:
            SetAssistantStatus("Searching...")
            from Backend.RealtimeSearchEngine import RealtimeSearchEngine
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        elif G:
            SetAssistantStatus("Thinking...")
            Answer = ChatBot(QueryModifier(Merged_query))
        elif R:
            SetAssistantStatus("Searching...")
            from Backend.RealtimeSearchEngine import RealtimeSearchEngine
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        else:
            for Queries in Decision:
                if "exit" in Queries.lower() or "bye" in Queries.lower():
                    Answer = f"Goodbye {Username}! Have a great day!"
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SaveToChatLog("assistant", Answer)
                    SetAssistantStatus("Speaking...")
                    try:
                        TextToSpeech(Answer)
                    except:
                        pass
                    sleep(2)
                    return True
        
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        SaveToChatLog("assistant", Answer)
        SetAssistantStatus("Speaking...")
        try:
            TextToSpeech(Answer)
        except:
            pass

    SetAssistantStatus("Ready")
    return False

# Monitoring thread for text input
import threading

def monitoring_thread():
    """Background thread to check for text and voice input."""
    while True:
        try:
            status = GetMicrophoneStatus()
            if status == "False":
                Query = handle_input()
                if Query:
                    SetMicrophoneStatus("True")
                    MainExecution(Query)
                    SetMicrophoneStatus("False")
            elif status == "True":
                # Voice recognition requested from GUI
                Query = SpeechRecognition()
                if Query and len(Query.strip()) > 1:
                    MainExecution(Query)
                SetMicrophoneStatus("False")
        except Exception as e:
            print(f"Monitor error: {e}")
        sleep(0.5)

if __name__ == "__main__":
    print("Main: Starting app...")
    
    # Start monitoring thread
    monitor = threading.Thread(target=monitoring_thread, daemon=True)
    monitor.start()
    
    print("Main: Starting GUI...")
    sys.stdout.flush()
    
    try:
        GraphicalUserInterface()
    except Exception as e:
        print(f"Main: GUI Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("Main: App closed")
