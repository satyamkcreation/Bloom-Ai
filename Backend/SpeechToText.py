"""
Speech-to-Text Module for Bloom AI
Uses Chrome WebSpeech API for voice recognition with fallback to text input
"""

import os
import platform
import sys

# Ensure Data directory exists
os.makedirs("Data", exist_ok=True)

# Load environment variables
try:
    from dotenv import dotenv_values
    env_vars = dotenv_values(".env")
    InputLanguage = env_vars.get("InputLanguage", "en-US")
except:
    InputLanguage = "en-US"

CURRENT_OS = platform.system()

# HTML for speech recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Voice Recognition</title>
    <style>
        body { font-family: Arial; background: #1a1a2e; color: white; padding: 20px; }
        #start, #end { padding: 10px 20px; margin: 5px; font-size: 16px; cursor: pointer; }
        #start { background: #00D4FF; border: none; border-radius: 5px; }
        #end { background: #ff4444; border: none; border-radius: 5px; }
        #output { margin-top: 20px; padding: 10px; font-size: 18px; min-height: 30px; }
        .status { color: #00D4FF; font-size: 14px; margin-top: 10px; }
    </style>
</head>
<body>
    <h2>Voice Recognition</h2>
    <button id="start" onclick="startRecognition()">Start Listening</button>
    <button id="end" onclick="stopRecognition()">Stop</button>
    <p id="output"></p>
    <p class="status" id="status">Click Start to begin listening...</p>
    
    <script>
        const output = document.getElementById('output');
        const status = document.getElementById('status');
        let recognition;
        let finalTranscript = '';
        
        function startRecognition() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                status.textContent = 'Speech recognition not supported in this browser.';
                return;
            }
            
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = 'en-US';
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.maxAlternatives = 1;
            
            recognition.onstart = function() {
                status.textContent = 'Listening... Speak now!';
            };
            
            recognition.onresult = function(event) {
                let interimTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }
                output.textContent = finalTranscript + interimTranscript;
            };
            
            recognition.onerror = function(event) {
                status.textContent = 'Error: ' + event.error;
            };
            
            recognition.onend = function() {
                if (finalTranscript) {
                    status.textContent = 'Done! Got: ' + finalTranscript;
                } else {
                    status.textContent = 'No speech detected. Click Start to try again.';
                }
            };
            
            recognition.start();
        }
        
        function stopRecognition() {
            if (recognition) {
                recognition.stop();
            }
        }
    </script>
</body>
</html>'''

# Write HTML file
voice_html_path = os.path.join("Data", "voice.html")
with open(voice_html_path, "w", encoding='utf-8') as f:
    f.write(HtmlCode)

# Build file URL
current_dir = os.getcwd()
if CURRENT_OS == "Windows":
    link = "file:///" + voice_html_path.replace("\\", "/")
else:
    link = "file:///" + voice_html_path

# Chrome options
chrome_options = None
try:
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=400,300")
except ImportError:
    chrome_options = None

# Driver reference
driver = None

def get_driver():
    """Lazily initialize Chrome driver."""
    global driver
    if driver is not None:
        return driver
    
    if chrome_options is None:
        raise Exception("Selenium Chrome options not available")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Chrome driver error: {e}")
        raise

# Temp directory path
TempDirPath = os.path.join(current_dir, "Frontend", "Files")

def SetAssistantStatus(Status):
    """Update the assistant status in the temp file."""
    try:
        os.makedirs(TempDirPath, exist_ok=True)
        with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as f:
            f.write(Status)
    except:
        pass

def QueryModifier(Query):
    """Modify query to be grammatically correct."""
    if not Query or not Query.strip():
        return ""
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['how', 'what', 'who', 'where', 'when', 'why', 'which', 'whose', 'whom', 
                      'can', 'do', 'is', 'are', 'will', 'should', "what's", "where's", "how's"]
    
    if any(word in new_query for word in question_words):
        if query_words[-1][-1] in ["?", ".", "!"]:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ["?", ".", "!"]:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()

def SpeechRecognition():
    """
    Main speech recognition function.
    Returns recognized text or empty string on failure.
    """
    SetAssistantStatus("Starting voice recognition...")
    
    # Try to use Chrome WebSpeech
    try:
        drv = get_driver()
        drv.get(link)
        
        # Wait for page to load
        import time
        time.sleep(1)
        
        # Click start button
        from selenium.webdriver.common.by import By
        drv.find_element(By.ID, "start").click()
        SetAssistantStatus("Listening...")
        
        # Wait for speech input (up to 30 seconds)
        timeout = 30
        start_time = time.time()
        last_text = ""
        
        while time.time() - start_time < timeout:
            try:
                text = drv.find_element(By.ID, "output").text
                if text and len(text.strip()) > 0:
                    last_text = text
                    # If we have final speech (wait a bit to confirm)
                    if time.time() - start_time > 3 and text == last_text:
                        drv.find_element(By.ID, "end").click()
                        SetAssistantStatus("Processing...")
                        return QueryModifier(text.strip())
                time.sleep(0.5)
            except:
                time.sleep(0.5)
        
        # Timeout - try to stop gracefully
        try:
            drv.find_element(By.ID, "end").click()
        except:
            pass
        
        if last_text:
            SetAssistantStatus("Processing...")
            return QueryModifier(last_text.strip())
        
        SetAssistantStatus("No speech detected")
        return ""
        
    except Exception as e:
        print(f"Speech recognition error: {e}")
        SetAssistantStatus("Voice recognition unavailable")
        return ""

# Alternative: Simple text-based input function
def TextInput(prompt="Enter your command: "):
    """Fallback text input function."""
    try:
        return input(prompt)
    except:
        return ""

# Test function
if __name__ == "__main__":
    print("Speech Recognition Test")
    print("=" * 40)
    
    # Test 1: Check if Chrome is available
    try:
        drv = get_driver()
        print("Chrome driver: OK")
        drv.quit()
    except Exception as e:
        print(f"Chrome driver: FAILED - {e}")
    
    # Test 2: Try speech recognition
    print("\nStarting speech recognition (will timeout in 10 seconds)...")
    result = SpeechRecognition()
    print(f"Result: {result if result else 'No speech detected'}")
