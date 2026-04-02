import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import dotenv_values
import os
from time import sleep

# Load environment variables
env_vars = dotenv_values('.env')
HuggingFaceAPIKey = env_vars.get("HuggingFaceAPIKey")

# Function to open and display images based on a given prompt
def open_images(prompt):
    folder_path = r"Data"  # Folder where images are stored
    prompt = prompt.replace(" ", "_")  # Replace spaces with underscores

    # Generate the filenames for the images
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            # Try to open the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Pause for 1 sec before showing next image

        except IOError:
            print(f"Unable to open {image_path}")

# API details for the Hugging Face stable diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

def get_headers():
    """Get API headers, checking for valid key."""
    if not HuggingFaceAPIKey or HuggingFaceAPIKey == "YOUR_HUGGINGFACE_TOKEN_HERE":
        print("WARNING: HuggingFaceAPIKey not set in .env file!")
        print("Get a free token at: https://huggingface.co/settings/tokens")
        return None
    return {"Authorization": f"Bearer {HuggingFaceAPIKey}"}

# Async function to send queries to Hugging Face through API
async def query(payload):
    headers = get_headers()
    if headers is None:
        print("Skipping image generation — no API key configured.")
        return b""
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Image generation API error: {response.status_code} - {response.text[:200]}")
        return b""
    return response.content

# Async function to generate images based on a prompt
async def generate_images(prompt: str):
    tasks = []

    # Create 4 image generation tasks
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=1k, sharpness=maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)

    # Save the generated images to the files
    os.makedirs("Data", exist_ok=True)
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:  # Only save non-empty responses
            filepath = fr"Data/{prompt.replace(' ', '_')}{i + 1}.jpg"
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            print(f"Saved image: {filepath}")

# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Main loop to check for image generation requests
if __name__ == "__main__":
    while True:
        try:
            # Read the prompt and status from the file
            with open(r"Frontend/Files/ImageGeneration.data", "r") as f:
                Data: str = f.read()
                prompt, status = Data.split(",")

            # If status indicates an image generation request
            if status.strip() == "True":
                print("Generating Images...")
                GenerateImages(prompt=prompt)

                # Reset the status in the file after generating image
                with open(r"Frontend/Files/ImageGeneration.data", "w") as f:
                    f.write("False,False")
                break  # Exit the loop after generating image

            else:
                sleep(1)  # Wait for 1 sec before checking again
        except Exception as e:
            print(f"ImageGeneration error: {e}")
            sleep(1)
