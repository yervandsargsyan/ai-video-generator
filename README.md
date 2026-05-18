# 🎬 AI Video Generator with Automated YouTube Upload

An end-to-end AI system that generates short videos from scratch and automatically uploads them to YouTube using the YouTube Data API.

The pipeline includes:
- Topic generation (LLM-based)
- Script generation and modification (LLM-based)
- Audio synthesis (TTS: local silero / google API)
- Image generation (replicate API)
- Video rendering (MoviePy)
- Subtitle generation 
- Automated upload to YouTube

---

#  Features

-  AI-powered script generation
-  Text-to-speech voice generation
-  Automated video assembly
-  Subtitle generation
-  Direct upload to YouTube via API
-  Fully automated pipeline
Note: Every component of the system supports both automated generation and manual input, enabling flexible control over the full pipeline.
---

# Architecture

Topic Generator → Script Engine → TTS Engine → Image Generator → Video Renderer → Subtitle Engine → YouTube Uploader

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```
## 2. Create virtual environment (recommended)
```bash
python -m venv venv
```
Activate venv:
Windows:
```bash
venv\Scripts\activate
```
Mac/Linux:
```bash
source venv/bin/activate
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Environment Variables (.env)

Create .env file in the root directory:
Enter your api keys
OPENAI_API_KEY=your_openai_key_here
ELEVENLABS_API_KEY=your_tts_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
GOOGLE_TTS_API_KEY=YOUR_GOOGLE_TTS_API_KEY (OPTIONAL)

# YouTube API Setup (IMPORTANT)
## 1. Create Google Cloud Project

Go to:
https://console.cloud.google.com/

Create a new project
Enable YouTube Data API v3

## 2. Create OAuth credentials

Go to:
APIs & Services → Credentials

Create OAuth Client ID
Application type: Desktop App
Download client_secrets.json

## 3. Place file in project root

# First authentication run

On first upload run:
```bash
python main.py
```

You will:

Open browser
Login to Google account
Allow permissions
Token will be saved automatically (token.json)


# Usage

Run full pipeline:
```bash
python main.py
``` 
Run a specific pipeline step (e.g. audio, text, video):
```bash
python -m pipeline.X
```
Run individual agent for testing:
```bash
python -m agents.X_agent
```

# Notes
client_secrets.json is required for YouTube OAuth upload  
.env must contain all API keys  
First run will trigger Google login authorization  
Token is stored locally after first authentication  
This is the public demo implementation of the full system.  
For access to the full extended version or collaboration inquiries, please feel free to contact me.  
Email: yervandsargsyan.w@gmail.com
# Demo

Fully AI-generated video:

👉 [https://youtube.com/...](https://www.youtube.com/shorts/DWUkEssVlng)

This video is generated automatically by the full pipeline:
no manual editing required.
