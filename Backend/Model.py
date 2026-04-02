from rich import print  # Import the Rich library to enhance the output of the terminal.
from dotenv import dotenv_values  # Import the dotenv_values library to load environment variables from a .env file.

# Load environment variables from a .env file.
env_vars = dotenv_values('.env')
# Retrieve the API key.
CohereAPIKey = env_vars.get("CohereAPIKey")

# Try to initialize Cohere client (optional — fallback works without it)
co = None
COHERE_AVAILABLE = False
try:
    if CohereAPIKey and CohereAPIKey != "1234567890abcdefghijklmnopqrstuvwxyz":
        import cohere
        co = cohere.ClientV2(api_key=CohereAPIKey)
        COHERE_AVAILABLE = True
        print("[green]Cohere API initialized successfully.[/green]")
    else:
        print("[yellow]Cohere API key not set or placeholder. Using keyword-based classifier.[/yellow]")
except Exception as e:
    print(f"[yellow]Cohere not available ({e}). Using keyword-based classifier.[/yellow]")

# Define a list of recognized function keywords for task categorization.
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "execute"
]

# Initialize an empty list to store user messages.
messages = []

# Define the preamble that guides the AI model on how to categorize queries
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
-> Respond with 'execute (command description)' if a query is asking to perform a computer action like creating files, folders, running terminal commands, managing files, etc. For example: 'create a folder on desktop' respond with 'execute create folder Desktop/new_folder', 'run dir command' respond with 'execute run dir', 'delete the test file' respond with 'execute delete file test.txt'.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

# Define a chat history with predefined user-chatbot interactions for context.
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that I have a dancing performance on 5th Aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th Aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."},
    {"role": "User", "message": "create a folder called my_project on the desktop"},
    {"role": "Chatbot", "message": "execute create folder Desktop/my_project"},
    {"role": "User", "message": "run the command ipconfig"},
    {"role": "Chatbot", "message": "execute run ipconfig"},
    {"role": "User", "message": "open notepad and create a file on desktop called notes.txt"},
    {"role": "Chatbot", "message": "open notepad, execute create file Desktop/notes.txt"},
]


def KeywordClassifier(prompt: str) -> list:
    """
    Keyword-based fallback classifier — works without any API.
    Classifies user intent based on keyword matching.
    """
    lower_prompt = prompt.lower().strip()

    # Exit detection
    if any(word in lower_prompt for word in ["exit", "bye", "goodbye", "quit", "shut down", "turn off", "see you"]):
        return ["exit"]

    results = []

    # Computer control / execute commands
    execute_keywords = [
        "create folder", "make folder", "create directory", "make directory",
        "create a folder", "make a folder", "create a directory", "make a directory",
        "create file", "make file", "create a file", "make a file",
        "delete file", "remove file", "delete a file", "remove a file",
        "delete folder", "remove folder", "delete a folder", "remove a folder",
        "move file", "move folder", "move a file", "move a folder",
        "copy file", "copy folder", "rename file", "rename folder",
        "run command", "execute command", "terminal command", "command line",
        "list files", "show files", "read file", "write to file",
        "create project", "make project", "new folder", "new file",
        "run the", "run this", "run ipconfig", "run ping", "run dir",
    ]
    # Also catch "run X" at the start of the prompt
    if lower_prompt.startswith("run ") or lower_prompt.startswith("execute "):
        results.append(f"execute {prompt}")
    if any(kw in lower_prompt for kw in execute_keywords):
        results.append(f"execute {prompt}")
    # Also detect verb + noun combos (e.g., "create a project folder on Desktop")
    elif not results:
        action_verbs = ["create", "make", "delete", "remove", "move", "copy", "rename"]
        target_nouns = ["folder", "directory", "file", "project"]
        has_verb = any(v in lower_prompt for v in action_verbs)
        has_noun = any(n in lower_prompt for n in target_nouns)
        if has_verb and has_noun:
            results.append(f"execute {prompt}")

    # Open detection
    if any(word in lower_prompt for word in ["open ", "launch ", "start "]):
        if "open " in lower_prompt:
            parts = lower_prompt.split("open ")
            for part in parts[1:]:
                app = part.split()[0].strip(",.!?") if part.split() else ""
                if app and app not in ["a", "the", "an", "file", "it"]:
                    results.append(f"open {app}")
        if not any(r.startswith("open") for r in results):
            results.append(f"open {prompt.split()[-1]}")

    # Close detection
    if any(word in lower_prompt for word in ["close ", "quit ", "kill "]):
        if "close " in lower_prompt:
            app = lower_prompt.split("close ")[1].split()[0].strip(",.!?")
            results.append(f"close {app}")

    # Play detection
    if any(word in lower_prompt for word in ["play ", "listen to "]):
        if "play " in lower_prompt:
            song = lower_prompt.split("play ")[1].strip()
            results.append(f"play {song}")

    # Image generation
    if any(word in lower_prompt for word in ["generate image", "create image", "draw ", "generate picture"]):
        if "image " in lower_prompt:
            prompt_text = lower_prompt.split("image ")[1] if "image " in lower_prompt else prompt
            results.append(f"generate image {prompt_text}")
        else:
            results.append(f"generate image {prompt}")

    # System controls
    if any(word in lower_prompt for word in ["volume", "sound", "mute", "unmute", "brightness"]):
        results.append(f"system {prompt}")

    # Search
    if any(word in lower_prompt for word in ["search google", "google search", "search for", "look up"]):
        results.append(f"google search {prompt}")

    if any(word in lower_prompt for word in ["search youtube", "youtube search", "find on youtube"]):
        results.append(f"youtube search {prompt}")

    # Realtime info
    if any(word in lower_prompt for word in ["news", "latest", "current", "today's", "price of", "stock", "weather"]):
        if not results:  # Only if no other action was detected
            results.append(f"realtime {prompt}")

    # Content writing
    if any(word in lower_prompt for word in ["write ", "compose ", "draft "]):
        if any(word in lower_prompt for word in ["email", "letter", "essay", "poem", "song", "code", "application", "note"]):
            results.append(f"content {prompt}")

    # Default: general query
    if not results:
        results.append(f"general {prompt}")

    return results


# Define the main function for decision-making on queries.
def FirstLayerDMM(prompt: str = "test"):
    # Add the user's query to the message list.
    messages.append({"role": "User", "content": f"{prompt}"})
    
    try:
        if not COHERE_AVAILABLE:
            # Use keyword classifier directly
            return KeywordClassifier(prompt)

        # Try Cohere API
        try:
            # Use the v2 chat API
            response_obj = co.chat(
                model='command-r-plus',
                messages=[
                    {"role": "system", "content": preamble},
                    *[{"role": "user" if h["role"] == "User" else "assistant", "content": h["message"]} for h in ChatHistory],
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=256,
            )
            
            # Extract the response text
            response = ""
            if hasattr(response_obj, 'message') and hasattr(response_obj.message, 'content'):
                for block in response_obj.message.content:
                    if hasattr(block, 'text'):
                        response += block.text
            
            if not response:
                return KeywordClassifier(prompt)

            # Remove newline characters and split the response into individual tasks.
            response = response.replace("\n", "")
            response = response.split(",")
            
            # Strip leading and trailing whitespaces from each task.
            response = [i.strip() for i in response]
            
        except Exception as e:
            print(f"Error with Cohere API: {e}")
            return KeywordClassifier(prompt)
        
        # Initialize an empty list to filter valid tasks.
        temp = []
        
        # Filter the tasks based on recognized function keywords.
        for task in response:
            for func in funcs:
                if task.startswith(func):
                    temp.append(task)  # Add valid tasks.
        
        # Update the response with the filtered tasks.
        response = temp
        
        # If no valid tasks were found, default to keyword classifier
        if not response:
            response = KeywordClassifier(prompt)
            
        # Return the filtered response.
        return response
    
    finally:
        pass

# Entry point for the script.
if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>> ")))  # Print the categorized response to the terminal.