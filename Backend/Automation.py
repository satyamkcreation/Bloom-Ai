from webbrowser import open as webopen  # Import web browser functionality.
from pywhatkit import search, playonyt  # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values  # Import dotenv to manage environment variables.
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing HTML content.
from rich import print  # Import rich for styled console output.
from groq import Groq  # Import Groq for AI chat functionalities.
import webbrowser  # Import webbrowser for opening URLs.
import subprocess  # Import subprocess for interacting with the system.
import requests  # Import requests for making HTTP requests.
import asyncio  # Import asyncio for asynchronous programming.
import platform  # Import platform for OS detection.
import os  # Import os for operating system functionalities.

# Detect OS
CURRENT_OS = platform.system()  # "Windows", "Darwin", "Linux"

# Load environment variables from the .env file
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")  # Retrieve the Groq API key
Username = env_vars.get("Username", "User")  # Load Username from .env

# Define CSS classes for parsing specific elements in HTML content
classes = [
    "zCubwf", "hgKElc", "LTKOO sY7ric", "ZOLcW", "gsrt vk_bk FzvWsb YwPhnf",
    "pclqee", "tw-Data-text tw-text-small tw-ta", "1Z6rdc", "05uR6d LTKOO",
    "V1zY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt",
    "sXLaOe", "LwkfKe", "VQF4g", "qviWpe", "kno-rdesc", "SPZz6b"
]

# Define a user-agent for making web requests
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Initialize the Groq client with the API key
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

# List to store chatbot messages
messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {Username}, You're a content writer. You have to write content like letter,codes,applications,essays,notes,songs,poems etc "}]


def GoogleSearch(Topic):
    search(Topic)  # Use pywhatkit's search function to perform a Google search
    return True  # Indicate success


# Function to generate content using AI and save it to a file.
def Content(Topic):
    # Nested function to open a file in the appropriate text editor (cross-platform).
    def OpenTextEditor(File):
        if CURRENT_OS == "Windows":
            subprocess.Popen(["notepad.exe", File])
        elif CURRENT_OS == "Darwin":
            subprocess.run(["open", "-a", "TextEdit", File])
        else:  # Linux
            # Try common text editors
            for editor in ["xdg-open", "gedit", "nano", "vi"]:
                try:
                    subprocess.Popen([editor, File])
                    return
                except FileNotFoundError:
                    continue

    # Nested function to generate content using the AI chatbot
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = "" 
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("content ", "")
    ContentByAI = ContentWriterAI(Topic)
    os.makedirs("Data", exist_ok=True)  # Ensure the "Data" directory exists
    filepath = f"Data/{Topic.lower().replace(' ', '')}.txt"
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    OpenTextEditor(filepath)
    return True

 
# Function to search YouTube.
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"  
    webbrowser.open(Url4Search)  
    return True  


# Function to play a video on YouTube.
def PlayYouTube(query):
    playonyt(query)  # Use pywhatkit's playonyt function to play the video
    return True  # Indicate success


# Function to open an application (cross-platform).
def OpenApp(app):
    try:
        app_lower = app.lower().strip()

        # Check if it's a known website
        websites = {
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "twitter": "https://www.twitter.com",
            "youtube": "https://www.youtube.com",
            "github": "https://www.github.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "linkedin": "https://www.linkedin.com",
            "reddit": "https://www.reddit.com",
            "whatsapp web": "https://web.whatsapp.com",
            "netflix": "https://www.netflix.com",
            "amazon": "https://www.amazon.com",
            "chatgpt": "https://chat.openai.com",
        }

        if app_lower in websites:
            webbrowser.open(websites[app_lower])
            return True

        if CURRENT_OS == "Windows":
            # Common Windows app name -> executable mapping
            win_apps = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "calc": "calc.exe",
                "paint": "mspaint.exe",
                "cmd": "cmd.exe",
                "terminal": "wt.exe",
                "powershell": "powershell.exe",
                "explorer": "explorer.exe",
                "file explorer": "explorer.exe",
                "chrome": "chrome.exe",
                "google chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "brave": "brave.exe",
                "vscode": "code.exe",
                "vs code": "code.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "powerpoint": "powerpnt.exe",
                "outlook": "outlook.exe",
                "discord": "discord.exe",
                "spotify": "spotify.exe",
                "telegram": "telegram.exe",
                "vlc": "vlc.exe",
                "settings": "ms-settings:",
            }

            if app_lower in win_apps:
                executable = win_apps[app_lower]
                if executable.startswith("ms-"):
                    os.startfile(executable)
                else:
                    subprocess.Popen(executable, shell=True)
            else:
                try:
                    os.startfile(app)
                except OSError:
                    subprocess.Popen(f'start "" "{app}"', shell=True)

        elif CURRENT_OS == "Darwin":
            subprocess.run(["open", "-a", app])

        else:  # Linux
            subprocess.Popen([app_lower], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return True
    except Exception as e:
        print(f"Error opening app: {e}")
        return False


def extract_Links(html):
    if html is None:
        return []
    soup = BeautifulSoup(html, 'html.parser')  # Parse the HTML content
    links = soup.find_all('a', {'jsname': 'UWckNb'})  # Find relevant links
    return [link.get('href') for link in links]  # Return the links


# Function to perform a Google search and retrieve HTML.
def search_google(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": useragent}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print("Error: Unable to fetch search results.")
        return None

# Function to close an application (cross-platform).
def CloseApp(app):
    try:
        app_lower = app.lower().strip()
        if CURRENT_OS == "Windows":
            # Windows process name mapping
            win_processes = {
                "notepad": "notepad",
                "calculator": "Calculator",
                "calc": "Calculator",
                "paint": "mspaint",
                "chrome": "chrome",
                "google chrome": "chrome",
                "firefox": "firefox",
                "edge": "msedge",
                "brave": "brave",
                "vscode": "Code",
                "vs code": "Code",
                "word": "WINWORD",
                "excel": "EXCEL",
                "discord": "Discord",
                "spotify": "Spotify",
                "telegram": "Telegram",
                "vlc": "vlc",
            }
            process_name = win_processes.get(app_lower, app_lower)
            result = subprocess.run(
                f'taskkill /F /IM "{process_name}.exe"',
                shell=True, capture_output=True, text=True
            )
            if result.returncode != 0:
                # Try with original name
                subprocess.run(
                    f'taskkill /F /IM "{app}.exe"',
                    shell=True, capture_output=True, text=True
                )
        elif CURRENT_OS == "Darwin":
            subprocess.run(["pkill", "-f", app], capture_output=True)
        else:  # Linux
            subprocess.run(["pkill", "-f", app_lower], capture_output=True)
        return True
    except Exception as e:
        print(f"Error closing app: {e}")
        return False


# Function to control system volume (cross-platform).
def System(command):
    command_lower = command.lower().strip()

    def mute():
        if CURRENT_OS == "Windows":
            subprocess.run(
                'powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"',
                shell=True, capture_output=True
            )
        elif CURRENT_OS == "Darwin":
            subprocess.run(["osascript", "-e", "set Volume 0"])
        else:
            subprocess.run(["amixer", "set", "Master", "mute"], capture_output=True)

    def unmute():
        if CURRENT_OS == "Windows":
            subprocess.run(
                'powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"',
                shell=True, capture_output=True
            )
        elif CURRENT_OS == "Darwin":
            subprocess.run(["osascript", "-e", "set Volume 5"])
        else:
            subprocess.run(["amixer", "set", "Master", "unmute"], capture_output=True)

    def volume_up():
        if CURRENT_OS == "Windows":
            subprocess.run(
                'powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"',
                shell=True, capture_output=True
            )
        elif CURRENT_OS == "Darwin":
            subprocess.run(["osascript", "-e", "set Volume output volume (output volume of (get volume settings) + 10)"])
        else:
            subprocess.run(["amixer", "set", "Master", "10%+"], capture_output=True)

    def volume_down():
        if CURRENT_OS == "Windows":
            subprocess.run(
                'powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"',
                shell=True, capture_output=True
            )
        elif CURRENT_OS == "Darwin":
            subprocess.run(["osascript", "-e", "set Volume output volume (output volume of (get volume settings) - 10)"])
        else:
            subprocess.run(["amixer", "set", "Master", "10%-"], capture_output=True)

    if "mute" in command_lower and "unmute" not in command_lower:
        mute()
    elif "unmute" in command_lower:
        unmute()
    elif "volume up" in command_lower or "vol up" in command_lower:
        volume_up()
    elif "volume down" in command_lower or "vol down" in command_lower:
        volume_down()
    else:
        return True


async def TranslateAndExecute(commands: list[str]):
    funcs = []  # List to store asynchronous tasks
    for command in commands:
        if command.startswith("open "):  # Handle "open" commands
            if "open file" in command:  # Ignore "open file" commands
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)
        elif command.startswith("general "):
            pass
        elif command.startswith("realtime "):
            pass
        elif command.startswith("close "):  # Handle "close" commands
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
        elif command.startswith("play "):  # Handle "play" commands
            fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play "))
            funcs.append(fun)
        elif command.startswith("content "):  # Handle "content" commands
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)
        elif command.startswith("google search "):  # Handle "google search" commands
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)
        elif command.startswith("youtube search "):  # Handle "youtube search" commands
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)
        elif command.startswith("system "):  # Handle "system" commands
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
        else:
            print(f"No function found for command: {command}")
    results = await asyncio.gather(*funcs)
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result


# Asynchronous function to automate command execution.
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True
