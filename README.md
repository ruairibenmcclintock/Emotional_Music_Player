# Emotional_Music_Player
This project demonstrates that conversational AI can be used to build a real-time, emotion-driven music recommendation system using current APIs and lightweight infrastructure.

## Installation
```bash
git clone https://github.com/ruairibenmcclintock/Emotional_Music_Player.git
cd Emotional_Music_Player
```

### Optionally, start a virtual environment
`python -m venv venv`

On Windows:
`venv\Scripts\activate`

Unix:
`source venv/bin/activate`

### Install dependencies
`pip install -r requirements.txt`

### Set up API keys
Spotify, LastFM and OpenAI API keys are required, to set them up, do the following:

In `spot_player.py`
```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
```

In `chatbot.py`
```
OPENAI_API_KEY=your_api_key
```

In `modd_music.py`
```
API_KEY=Last.Fm_api_here
```

### Running the app
`python gui.py`

## Description
This Project was for my Final year project in Electronic Engineering in MTU (Munster Technological University previously known as CIT) In Cork, Ireland. 
This project presents the development of an emotion-based music player that uses ChatGPT for conversational mood detection and integrates Last.fm for mood-tagged music recommendation. The system allows users to describe how they feel in natural language, extracts their emotional state through a structured prompt, and maps it to weighted mood tags. These tags are used to generate a song list, which is then queued for playback using the Spotify API.
A modular design was implemented to separate the chatbot, music selection, and playback functions, ensuring flexibility and ease of maintenance. A custom GUI was developed to manage user input and system feedback, with integrated logging for validation and debugging.
Testing confirmed that the system successfully handled a range of emotional inputs, generated valid JSON outputs, and returned accurate music matches. Errors such as invalid input, missing files, or Spotify issues were handled gracefully. Limitations included the system’s inability to resolve vague or off-topic responses and a lack of long-term user adaptation.
