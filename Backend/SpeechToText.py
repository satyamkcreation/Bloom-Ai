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
        #output { margin-top: 20px; padding: 10px; font-size: 18px; min-height: 30px; border: 1px solid #444; }
        .status { color: #00D4FF; font-size: 14px; margin-top: 10px; }
        #error { color: #ff4444; font-size: 12px; margin-top: 5px; }
    </style>
</head>
<body>
    <h2>Voice Recognition</h2>
    <button id="start" onclick="startRecognition()">Start Listening</button>
    <button id="end" onclick="stopRecognition()">Stop</button>
    <div id="output"></div>
    <div class="status" id="status">Ready</div>
    <div id="error"></div>
    
    <script>
        const output = document.getElementById('output');
        const status = document.getElementById('status');
        const errorDiv = document.getElementById('error');
        let recognition;
        
        function startRecognition() {
            try {
                if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                    status.textContent = 'Not supported';
                    errorDiv.textContent = 'Speech recognition not supported in this browser.';
                    return;
                }
                
                recognition = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
                recognition.lang = 'en-US';
                recognition.continuous = true;
                recognition.interimResults = true;
                
                recognition.onstart = () => { status.textContent = 'Listening'; errorDiv.textContent = ''; };
                recognition.onerror = (event) => { 
                    status.textContent = 'Error'; 
                    errorDiv.textContent = 'Recognition error: ' + event.error;
                };
                recognition.onend = () => { status.textContent = 'Ended'; };
                
                recognition.onresult = (event) => {
                    let combined = '';
                    for (let i = 0; i < event.results.length; i++) {
                        combined += event.results[i][0].transcript;
                    }
                    output.textContent = combined;
                };
                
                recognition.start();
            } catch (e) {
                errorDiv.textContent = 'JS Error: ' + e.message;
            }
        }
        
        function stopRecognition() {
            if (recognition) recognition.stop();
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
    
    try:
        drv = get_driver()
        drv.get(link)
        
        import time
        time.sleep(0.5) # Wait for load
        
        from selenium.webdriver.common.by import By
        drv.find_element(By.ID, "start").click()
        SetAssistantStatus("Listening...")
        
        timeout = 20
        start_time = time.time()
        last_text = ""
        last_change_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check status and errors
                cur_status = drv.find_element(By.ID, "status").text
                if "Error" in cur_status:
                    err_msg = drv.find_element(By.ID, "error").text
                    print(f"Speech JS Error: {err_msg}")
                    break
                    
                text = drv.find_element(By.ID, "output").text.strip()
                
                if text != last_text:
                    last_text = text
                    last_change_time = time.time()
                
                # If we have text and user hasn't spoken for 2 seconds, consider it done
                if last_text and (time.time() - last_change_time > 2.0):
                    break
                    
                time.sleep(0.3)
            except Exception as e:
                time.sleep(0.3)
        
        # Stop 
        try:
            drv.find_element(By.ID, "end").click()
        except:
            pass
            
        if last_text:
            SetAssistantStatus("Processing...")
            return QueryModifier(last_text)
        
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
