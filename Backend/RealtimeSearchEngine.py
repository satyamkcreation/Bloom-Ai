from googlesearch import search # pip install google
from groq import Groq # pip install groq
from json import load, dump  # json library
import datetime # datetime python library
from dotenv import dotenv_values  # dotenv library to load environment variables

# Load environment variables from .env file
env_vars = dotenv_values(".env")

# Retrieve specific environment variables
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client with API key
client = Groq(api_key=GroqAPIKey) 

# System message template for the chatbot
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Load chat log from file or create a new one if it doesn't exist
try:
    with open(r"Data/ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data/ChatLog.json", "w") as f:
        dump([], f)

# Function to perform Google search and format the results
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return Answer

# Function to remove empty lines from the answer
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Initial system and user messages for the chatbot
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get current date and time information
def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds.\n"
    return data

# Main function to handle real-time search and generate responses
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load chat log from file
    with open(r"Data/ChatLog.json", "r") as f:
        messages = load(f)

    # Append user prompt to messages
    messages.append({"role": "user", "content": f"{prompt}"})

    try:
        # Perform Google search and append the result to SystemChatBot
        search_results = GoogleSearch(prompt)
        SystemChatBot.append({"role": "system", "content": search_results})

        # Generate response using Groq client
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )

            Answer = ""

            # Collect response chunks
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    Answer += chunk.choices[0].delta.content
        except Exception as e:
            print(f"Error with Groq API: {e}")
            # Improved fallback response if API fails
            Answer = f"I searched for information about '{prompt}' and found some results, but I'm having trouble analyzing them right now. You can try opening a web browser and searching directly, or ask me to 'open google' and I can help you with that."

        # Clean up the answer
        Answer = Answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat log to file
        with open(r"Data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        # Remove the last system message from SystemChatBot
        SystemChatBot.pop()
        return AnswerModifier(Answer=Answer)
    except Exception as e:
        print(f"Error in RealtimeSearchEngine: {e}")
        return f"I'm sorry, I encountered an error while searching for information about '{prompt}'. Please try again later."

# Main entry point of the program for interactive querying
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))