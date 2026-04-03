"""
Backend/Model.py
Decision-Making Model (DMM) for Bloom AI
Decides whether a query is 'general', 'realtime', 'open', 'close', 'execute', etc.
Uses Groq (Llama 3.3) for intelligence with a local keyword fallback.
"""

from rich import print
from dotenv import dotenv_values
import os
import json

# Load environment variables
env_vars = dotenv_values('.env')
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = None
GROQ_AVAILABLE = False
try:
    if GroqAPIKey and len(GroqAPIKey) > 20:
        from groq import Groq
        client = Groq(api_key=GroqAPIKey)
        GROQ_AVAILABLE = True
        print("[green]Groq DMM initialized successfully.[/green]")
    else:
        print("[yellow]Groq API key not set. Using keyword-based classifier.[/yellow]")
except Exception as e:
    print(f"[yellow]Groq not available ({e}). Using keyword-based classifier.[/yellow]")

# Recognized function keywords
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "execute"
]

# The preamble to guide the LLM
preamble = """
You are a high-speed Decision-Making Model for a computer assistant.
Your ONLY job is to categorize the user's query into one or more tasks.
Current tasks: general, realtime, open, close, play, generate image, system, content, google search, youtube search, reminder, execute.

RULES:
1. 'general (query)': Chatting, greetings, basic knowledge (who is Akbar?), time/date.
2. 'realtime (query)': Latest news, current events, weather, profiles of people (who is Salman Khan?).
3. 'open (app/site)': Launching programs.
4. 'close (app)': Quitting programs.
5. 'play (song)': Music requests.
6. 'execute (cmd)': AUTOMATION like "create folder Desktop/test", "run dir", "delete file X".
7. 'generate image (prompt)': Image generation.
8. 'system (mute/unmute/volume)': OS controls.

RESPOND ONLY WITH THE CATEGORIZED TASKS SEPARATED BY COMMAS.
Example User: "Who is the PM of India and open chrome"
Example Assistant: "realtime who is the PM of India, open chrome"

Example User: "Create a folder on desktop"
Example Assistant: "execute create folder Desktop/new_folder"
"""

def KeywordClassifier(prompt: str) -> list:
    """Robust local keyword fallback for zero-latency categorization."""
    lower_prompt = prompt.lower().strip()
    
    # Exit detection
    if any(word in lower_prompt for word in ["exit", "bye", "goodbye", "quit", "shut down"]):
        return ["exit"]

    results = []

    # Computer control / automation
    action_verbs = ["create", "make", "delete", "remove", "move", "copy", "rename", "run", "execute"]
    target_nouns = ["folder", "directory", "file", "project", "command", "app", "application", "script"]
    has_action = any(v in lower_prompt for v in action_verbs)
    has_target = any(n in lower_prompt for n in target_nouns)
    
    if (has_action and has_target) or lower_prompt.startswith(("run ", "execute ")):
        results.append(f"execute {prompt}")

    # Navigation/Opening
    if any(w in lower_prompt for w in ["open ", "launch ", "start "]):
        if not any(r.startswith("execute") for r in results):
            app = lower_prompt.replace("open ", "").replace("launch ", "").replace("start ", "").strip()
            if app: results.append(f"open {app}")

    # Closing
    if any(w in lower_prompt for w in ["close ", "quit ", "kill "]):
        app = lower_prompt.replace("close ", "").replace("quit ", "").replace("kill ", "").strip()
        if app: results.append(f"close {app}")

    # Search (Google/Youtube)
    if "youtube" in lower_prompt:
        results.append(f"youtube search {prompt}")
    elif any(w in lower_prompt for w in ["google", "search for ", "look up "]):
        results.append(f"google search {prompt}")

    # Realtime fallback (names, news)
    if any(w in lower_prompt for w in ["news", "weather", "today", "who is ", "what is the price of"]):
        if not results: results.append(f"realtime {prompt}")

    # Play
    if "play " in lower_prompt:
        song = lower_prompt.split("play ")[1].strip()
        results.append(f"play {song}")

    # Default to general
    if not results:
        results.append(f"general {prompt}")

    return results

def FirstLayerDMM(prompt: str = "test"):
    """Main decision entry point."""
    if not prompt or len(prompt.strip()) < 2:
        return ["general ..."]

    # Try Groq for smart categorization
    if GROQ_AVAILABLE and client:
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": preamble},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.1 # Low temperature for accurate categorization
            )
            response = completion.choices[0].message.content.strip()
            
            # Parse comma separated results
            tasks = [t.strip() for t in response.split(",")]
            
            # Validation
            valid_tasks = []
            for t in tasks:
                if any(t.startswith(f) for f in funcs):
                    valid_tasks.append(t)
            
            if valid_tasks:
                return valid_tasks
        except Exception as e:
            print(f"[yellow]Groq DMM error, falling back to keywords: {e}[/yellow]")

    # Fallback to keyword classifier
    return KeywordClassifier(prompt)

if __name__ == "__main__":
    while True:
        p = input("DMM Test >>> ")
        if not p: break
        print(FirstLayerDMM(p))