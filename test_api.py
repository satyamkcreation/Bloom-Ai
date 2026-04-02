import os
from dotenv import dotenv_values
from groq import Groq
import cohere

env_vars = dotenv_values(".env")
groq_key = env_vars.get("GroqAPIKey")
cohere_key = env_vars.get("CohereAPIKey")

print(f"Groq Key: '{groq_key}'")
print(f"Cohere Key: '{cohere_key}'")

print("\nTesting Groq...")
try:
    client = Groq(api_key=groq_key.strip() if groq_key else "")
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=10
    )
    print("Groq Success!")
except Exception as e:
    print(f"Groq Failure: {e}")

print("\nTesting Cohere...")
try:
    co = cohere.ClientV2(api_key=cohere_key.strip() if cohere_key else "")
    response = co.chat(
        model='command-r-plus',
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=10
    )
    print("Cohere Success!")
except Exception as e:
    print(f"Cohere Failure: {e}")
