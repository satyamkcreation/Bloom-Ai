from groq import Groq  # Importing the Groq library
import json  # Importing JSON library for reading and writing JSON files
import datetime  # Importing datetime library for date and time operations
from dotenv import dotenv_values  # Importing dotenv library to load environment variables

# Loading environment variables from .env file
env_vars = dotenv_values(".env")

# Getting the username, assistant name, and API key from the environment variables
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Bloom")
GroqAPIKey = env_vars.get("GroqAPIKey", "")

# Initializing the Groq client with the API key (handle invalid keys gracefully)
client = None
API_AVAILABLE = False
if GroqAPIKey and not GroqAPIKey.startswith("YOUR_") and len(GroqAPIKey) > 20:
    try:
        client = Groq(api_key=GroqAPIKey)
        API_AVAILABLE = True
    except Exception as e:
        print(f"Groq API init error: {e}")

# List to store chatbot messages
messages = []

# Predefined system message for the chatbot
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# System message in the format required by the chatbot
SystemChatBot = [
    {"role": "system", "content": System}
]

# Try to load the chat log from a JSON file, if it doesn't exist, create an empty one
messages = []
try:
    with open(r"Data/ChatLog.json", "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content:
            messages = json.loads(content)
except (FileNotFoundError, json.JSONDecodeError, Exception):
    messages = []
    try:
        with open(r"Data/ChatLog.json", "w", encoding="utf-8") as f:
            json.dump([], f)
    except:
        pass

# Function to get real-time information
def Realtimelnformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds.\n"
    return data

# Function to modify the answer by removing empty lines
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Local fallback chatbot - works without API for common queries
def _local_response(query: str, assistantname: str, username: str) -> str:
    """Local fallback chatbot - works without API for common queries."""
    q = query.lower().strip()
    
    # Greetings
    greetings = ["hello", "hi", "hey", "good morning", "good evening", "good night", "greetings"]
    if any(w in q for w in greetings):
        return f"Hello {username}! I'm {assistantname}, your personal AI assistant. How may I help you today?"
    
    # How are you
    how_are_you = ["how are you", "how do you do", "how's it going", "how do you feel"]
    if any(w in q for w in how_are_you):
        return f"I'm doing excellently, {username}! I'm here and ready to assist you with any task. What would you like me to do?"
    
    # What's your name / Who are you
    who_are_you = ["what's your name", "who are you", "what are you", "your name", "what should i call you"]
    if any(w in q for w in who_are_you):
        return f"I am {assistantname}, an advanced AI assistant designed to help you with tasks, answer questions, and control your computer through voice commands."
    
    # Capabilities
    if any(w in q for w in ["what can you do", "your capabilities", "help me", "features", "help with"]):
        return f"I can help you with: Opening and closing applications, searching the web, generating images, creating files and folders, playing music on YouTube, controlling system settings like volume, and answering general questions. Just tell me what you need!"
    
    # Thanks
    if any(w in q for w in ["thank", "thanks", "thankyou"]):
        return f"You're welcome, {username}! Is there anything else I can help you with?"
    
    # Goodbye
    if any(w in q for w in ["bye", "goodbye", "see you", "exit", "later"]):
        return f"Goodbye, {username}! Feel free to call on me whenever you need assistance."
    
    # What's up
    if any(w in q for w in ["what's up", "sup", "wassup", "whats up"]):
        return f"Nothing much! I'm here and ready to help you, {username}. Just let me know what you need."
    
    # Who made you / Who created you
    if any(w in q for w in ["who made you", "who created you", "who built you", "your creator", "who developed you"]):
        return f"I was created as part of the Bloom AI project. I'm designed to be your personal AI assistant, ready to help with any task you throw at me!"
    
    # Jokes
    if any(w in q for w in ["joke", "funny", "make me laugh", "tell me something funny"]):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my computer I needed a break, and it hasn't stopped since.",
            "Why did the AI cross the road? To optimize your productivity on the other side!",
            "My creator made me smart, but I still can't figure out why humans need sleep!"
        ]
        import random
        return f"{random.choice(jokes)} Is there anything else I can help with?"
    
    # Weather (basic)
    if any(w in q for w in ["weather", "temperature", "is it hot", "is it cold"]):
        return f"I don't have access to live weather data right now, {username}. But I'm always ready to help you check the weather online! Would you like me to search for weather information?"
    
    # Time/Date
    if any(w in q for w in ["what time", "what's the time", "current time", "tell me the time"]):
        info = Realtimelnformation()
        return f"The current time is {info.split('Time: ')[1].split('.')[0]}, {username}."
    
    # Default response
    return f"I understand you're asking about '{query}'. Try asking me to 'open an app', 'search the web', 'create a file', or 'play music'. For more complex questions, please check your internet connection."

# Function to handle the chatbot interaction
def ChatBot(Query):
    """This function sends the user's query to the chatbot and returns the AI's response."""
    global messages
    
    # First try local response for simple queries (faster, no API needed)
    simple_queries = ["hello", "hi", "hey", "how are you", "what's your name", "bye", "thanks", "thank you"]
    if any(q in Query.lower() for q in simple_queries):
        Answer = _local_response(Query, Assistantname, Username)
        if any(word in Query.lower() for word in ["time", "day", "date", "year", "month"]):
            Answer += f"\n\n{Realtimelnformation()}"
        return Answer
    
    # Try API if available
    if not API_AVAILABLE or client is None:
        Answer = _local_response(Query, Assistantname, Username)
        if any(word in Query.lower() for word in ["time", "day", "date", "year", "month"]):
            Answer += f"\n\n{Realtimelnformation()}"
        return Answer
    
    retry_count = 0
    max_retries = 2
    
    while retry_count <= max_retries:
        try:
            # Load the chat log from the JSON file
            try:
                with open(r"Data/ChatLog.json", "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        messages = load(content)
            except:
                messages = []

            # Append the user's query to the messages
            messages.append({"role": "user", "content": f"{Query}"})

            try:
                # Create a completion request to the Groq API
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=SystemChatBot + [{"role": "system", "content": Realtimelnformation()}] + messages[-10:],  # Keep last 10 messages
                    max_tokens=1024,
                    temperature=0.7,
                    top_p=1,
                    stream=True,
                    stop=None
                )

                Answer = ""

                # Collect the response from the API
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        Answer += chunk.choices[0].delta.content

                # Clean the answer
                Answer = Answer.replace("</s>", "")

            except Exception as api_error:
                print(f"API error: {api_error}")
                # Enhanced local fallback
                Answer = _local_response(Query, Assistantname, Username)
                
                if any(word in Query.lower() for word in ["time", "day", "date", "year", "month"]):
                    Answer += f"\n\n{Realtimelnformation()}"

            # Append the assistant's response to the messages
            messages.append({"role": "assistant", "content": Answer})

            # Save the updated chat log to the JSON file
            try:
                with open(r"Data/ChatLog.json", "w", encoding="utf-8") as f:
                    dump(messages, f, indent=4)
            except:
                pass

            # Return the modified answer
            return AnswerModifier(Answer=Answer)

        except Exception as e:
            print(f"ChatBot error: {e}")
            retry_count += 1
            
            if retry_count > max_retries:
                return _local_response(Query, Assistantname, Username)
            
            # Try to reset the chat log before retrying
            try:
                with open(r"Data/ChatLog.json", "w", encoding="utf-8") as f:
                    dump([], f)
                messages = []
            except:
                pass

# Main loop to interact with the user
if __name__ == "__main__":
    print(f"Bloom AI Chatbot - Running in terminal mode")
    print(f"Assistant: {Assistantname} | User: {Username}")
    print(f"API Available: {API_AVAILABLE}")
    print("Type 'exit' to quit\n")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                print(f"{Assistantname}: Goodbye! Have a great day!")
                break
            response = ChatBot(user_input)
            print(f"{Assistantname}: {response}\n")
        except KeyboardInterrupt:
            print(f"\n{Assistantname}: Goodbye!")
            break
