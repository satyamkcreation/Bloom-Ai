# Bloom AI

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge">
</p>

<p align="center">
  <img src="Frontend/Graphics/Jarvis.gif" width="400" alt="Bloom AI Demo">
</p>

> A powerful JARVIS-style voice-controlled AI Assistant with a stunning dark-themed GUI, powered by modern AI APIs.

## Features

Bloom AI is a comprehensive AI assistant that combines voice recognition, natural language processing, and system automation to create an intelligent assistant experience.

### Core Capabilities

| Feature | Description |
|---------|-------------|
| 🎙️ **Voice Recognition** | Speech-to-text using Chrome WebSpeech API |
| 🔊 **Text-to-Speech** | Natural voice output using Edge TTS |
| 💬 **AI Chatbot** | Conversational AI powered by Groq LLM API |
| 🌐 **Real-time Search** | Google search with AI-powered responses |
| 🖼️ **Image Generation** | Create images from text using Stable Diffusion |
| 📱 **App Control** | Open/close applications and websites |
| 💻 **Computer Commands** | File/folder creation, deletion, and management |
| 🎵 **YouTube Integration** | Play music and search videos |
| 🔍 **Web Search** | Google and YouTube search automation |
| ⚙️ **System Controls** | Volume adjustment, mute/unmute |
| ✍️ **Content Generation** | Write emails, essays, code, and more |

### Supported Commands

```
"Open Notepad"              → Opens Notepad
"Play despacito"            → Plays song on YouTube  
"Search for Python tutorials" → Google search
"Generate image of a lion"  → Creates AI image
"Create folder my_project"  → Creates folder on Desktop
"Set reminder at 9pm"       → Sets a reminder
"What's the weather?"       → Real-time search
"Write an email"            → Content generation
```

## Tech Stack

- **Language**: Python 3.10+
- **GUI**: PyQt5
- **LLM APIs**: Groq, Cohere
- **Image Generation**: Hugging Face Stable Diffusion
- **Voice**: Edge TTS, Selenium WebSpeech
- **Automation**: PyWhatKit, BeautifulSoup

## Installation

### Prerequisites

- Python 3.10 or higher
- Google Chrome (for voice recognition)
- API Keys (see below)

### Clone & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/Bloom-Ai.git
cd Bloom-Ai

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r Requirements.txt
```

### API Keys Setup

Create a `.env` file in the root directory:

```env
# Required
Username=YourName
Assistantname=Bloom
GroqAPIKey=your_groq_api_key

# Optional (for enhanced features)
CohereAPIKey=your_cohere_api_key
HuggingFaceAPIKey=your_huggingface_token
InputLanguage=en-US
AssistantVoice=en-US-AriaNeural
```

**Get Free API Keys:**
- [Groq](https://console.groq.com/) - LLM chatbot
- [Cohere](https://cohere.com/) - Decision-making model
- [Hugging Face](https://huggingface.co/) - Image generation

## Usage

### Run the Application

```bash
python Main.py
```

### GUI Controls

- **Microphone Button**: Toggle voice input
- **Text Input**: Type commands directly
- **Send Button**: Submit your command
- **Window Controls**: Minimize, maximize, close

### Programmatic Usage

```python
from Backend.Chatbot import ChatBot
from Backend.Automation import OpenApp, GoogleSearch
from Backend.ImageGeneration import GenerateImages

# Chat with AI
response = ChatBot("Hello, how are you?")

# Open applications
OpenApp("notepad")

# Search Google
GoogleSearch("Python tutorials")

# Generate images
GenerateImages("a sunset over mountains")
```

## Project Structure

```
Bloom-Ai/
├── Main.py                 # Entry point
├── Requirements.txt       # Dependencies
├── .env                   # Environment variables
│
├── Backend/
│   ├── Model.py           # Decision-making engine
│   ├── Chatbot.py         # AI conversation
│   ├── TextToSpeech.py    # Voice output
│   ├── SpeechToText.py    # Voice input
│   ├── ComputerControl.py # System automation
│   ├── Automation.py      # Task execution
│   ├── RealtimeSearchEngine.py # Web search
│   └── ImageGeneration.py # AI image creation
│
├── Frontend/
│   ├── GUI.py             # PyQt5 interface
│   ├── Graphics/          # UI assets
│   └── Files/             # Temporary data
│
└── Data/
    ├── ChatLog.json       # Conversation history
    └── speech.mp3        # TTS audio cache
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (PyQt5)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   GUI.py    │  │ Voice Wave   │  │ Chat Bubbles │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
                    IPC Files
                         │
┌────────────────────────▼────────────────────────────────┐
│                    Main.py (Orchestrator)               │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │ Input Handler│─▶│ Decision   │─▶│ Task Executor │  │
│  └──────────────┘  │   Maker    │  └────────────────┘  │
│                    └─────────────┘                       │
└────────────────────────┬────────────────────────────────┘
                        │
┌────────────────────────▼────────────────────────────────┐
│                      Backend                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │  Chatbot │ │ Realtime │ │ Computer │ │  Image    │  │
│  │  (Groq)  │ │  Search  │ │  Control │ │ Generation│  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
│  ┌──────────┐ ┌──────────┐                             │
│  │    TTS   │ │   STT    │                             │
│  └──────────┘ └──────────┘                             │
└─────────────────────────────────────────────────────────┘
```

## Demo Commands

Try these commands to explore Bloom AI:

```text
"Hello Bloom"
"Open YouTube"
"Play faded by alan walker"
"Search for machine learning"
"Generate image of a futuristic city"
"Create folder called Projects on Desktop"
"What's the capital of France?"
"Set volume to 50%"
"Thank you, goodbye"
```

## Troubleshooting

### Voice Recognition Not Working
- Ensure Google Chrome is installed
- Allow microphone permissions in browser
- Check if Selenium ChromeDriver is available

### API Errors
- Verify API keys in `.env` file
- Check internet connection
- Ensure API keys have sufficient credits

### GUI Not Launching
- Install PyQt5: `pip install PyQt5`
- Check display settings (Linux may need X11)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by JARVIS from Iron Man
- Built with modern AI technologies
- Thanks to all API providers

---

<p align="center">
  Made with ❤️ by <a href="https://github.com">Your Name</a>
</p>

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=Bloom-Ai&label=Views&color=00D4FF" alt="Profile views">
</p>
