from groq import Groq
import os
from dotenv import load_dotenv


def load_groq():
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise RuntimeError("need to set GROQ_API_KEY")

    client = Groq(api_key=GROQ_API_KEY)
    return client

def load_replicate():
    load_dotenv()
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    if not REPLICATE_API_TOKEN:
        raise RuntimeError("need to set REPLICATE_API_TOKEN")

def load_google_tts():
    load_dotenv()
    try:
        from google.cloud import texttospeech

        return texttospeech.TextToSpeechClient(
            client_options={"api_key": os.getenv("GOOGLE_TTS_API_KEY")}
        )
    except Exception as e:
         raise RuntimeError("need to set GOOGLE_TTS_API_KEY")
