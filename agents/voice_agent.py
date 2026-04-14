from pathlib import Path
import torch
import soundfile as sf
import numpy as np
import re
from silero_stress import load_accentor
from utils.logger import logger
from config import config
from google.cloud import texttospeech
from config import config
from utils.logger import logger
from agents.api_loader import load_google_tts


def load_tts_model():
    """
    Loads the TTS model once at startup.
    Returns model and accentor.
    """
    try:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using Device: {device}")
        
        model, _ = torch.hub.load(
            repo_or_dir=config.path.siero_model_dir,
            model=config.audio.tts_model,
            language=config.audio.tts_language,
            speaker=config.audio.tts_model_id
        )
        model.to(device)
        accentor = load_accentor()
        
        return model, accentor, device
    except Exception as e:
        logger.error(f"Failed to load TTS model: {e}")
        raise RuntimeError("Unable to load TTS model") from e


# Load model once at module level
try:
    tts_model, accentor, device = load_tts_model()
except RuntimeError:
    tts_model, accentor, device = None, None, None
    logger.error("TTS model not loaded - voice generation will fail")


def add_pauses(audio_segments, 
               sample_rate = config.audio.pause_sample_rate, 
               pause_duration = config.audio.pause_duration):
    """
    Adds pauses after each audio segment.
    audio_segments: list of np.array
    sample_rate: sample rate
    pause_duration: pause duration in seconds
    """
    pause = np.zeros(int(sample_rate * pause_duration), dtype=np.float32)
    output = []

    for segment in audio_segments:
        output.append(segment)
        output.append(pause)

    return np.concatenate(output)

def apply_fade(audio: np.ndarray, sample_rate: int, fade_ms: int = 20) -> np.ndarray:
    fade_samples = int(sample_rate * fade_ms / 1000)
    
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    audio = audio.copy()
    audio[:fade_samples] *= fade_in
    audio[-fade_samples:] *= fade_out
    return audio

def split_text(text, min_chars = config.audio.tts_chunk_size):
    """
    Breaks the text into sentences, then combines sentences that are too short
    with adjacent ones so that each block is at least min_chars characters long.
    """
    # Break text into sentences
    sentences = re.split(r'(?<=[.!?—–]) +', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current = ""
    for s in sentences:
        if len(current) < min_chars:
            # Adding to current block
            if current:
                current += " " + s
            else:
                current = s
        else:
            # Saving
            chunks.append(current.strip())
            current = s

    if current:
        chunks.append(current.strip())

    return chunks


def generate_voice(script: str, output_dir: str = config.path.audio_dir) -> str:
    """
    Generates voice audio from the given script using pre-loaded TTS model.
    
    Args:
        script: Text to convert to speech
        output_dir: Directory to save the output audio file
        
    Returns:
        Path to the generated audio file
        
    Raises:
        RuntimeError: If model is not loaded or TTS generation fails
    """
    
    if tts_model is None:
        raise RuntimeError("TTS model is not loaded. Cannot generate voice.")
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    audio_path = Path(output_dir) / "voice.wav"

    try:
        chunks = split_text(script)
        logger.info(f"Text split into {len(chunks)} chunks")

        audio_segments = []

        for chunk in chunks:
            logger.info(f"Generating audio for chunk: {chunk[:50]}...")
            # apply_tts call
            audio = tts_model.apply_tts(
                text=accentor(chunk),
                speaker=config.audio.tts_speaker,
                sample_rate=config.audio.sample_rate_local
            )
            audio_segments.append(audio)

        full_audio = add_pauses(audio_segments)

        sf.write(str(audio_path), full_audio, config.audio.sample_rate_local)
        logger.info(f"Audio created: {audio_path}")

    except Exception as e:
        logger.error(f"TTS Error: {e}")
        raise

    return str(audio_path)


def add_ssml_breaks(text: str) -> str:
    text = text.replace(',', ' ,-')
    text = text.replace(':', ' <break time="30ms"/>')
    text = text.replace(';', ' <break time="30ms"/>')
    text = text.replace('?', ' ?-')
    text = text.replace('«', '').replace('»', '')
    return text

def generate_voice_google_api(script: str, output_dir: str = config.path.audio_dir) -> str:
    """
    Generates voice audio from the given script using Google Cloud TTS.
    
    Args:
        script: Text to convert to speech
        output_dir: Directory to save the output audio file
        
    Returns:
        Path to the generated audio file
        
    Raises:
        RuntimeError: If TTS generation fails
    """
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    audio_path = Path(output_dir) / "voice.wav"
    script = add_ssml_breaks(script)
    try:
        client = load_google_tts()
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=config.audio.google_tts_language_code,
            name=config.audio.google_tts_voice,
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=1.0,
        )

        chunks = split_text(script)
        logger.info(f"Text split into {len(chunks)} chunks")

        audio_segments = []

        for chunk in chunks:
            logger.info(f"Generating audio for chunk: {chunk}...")

            ssml_text = f'<speak><prosody rate="105%" volume="+1dB">{chunk}</prosody></speak>'
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
            
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Convert bytes to numpy array
            audio_np = np.frombuffer(response.audio_content, dtype=np.int16).astype(np.float32) / 32768.0
            audio_np = apply_fade(audio_np, config.audio.sample_rate_api)
            audio_segments.append(audio_np)

        full_audio = add_pauses(audio_segments)

        sf.write(str(audio_path), full_audio, config.audio.sample_rate_api)
        logger.info(f"Audio created: {audio_path}")

    except Exception as e:
        logger.error(f"TTS Error: {e}")
        raise

    return str(audio_path)


if __name__ == "__main__":
    test_text = """Привет! Это тестовая фраза для проверки генерации голоса. 
    Мы хотим убедиться, что все работает правильно."""
    generate_voice(test_text, "test_voice_local.wav")
    generate_voice_google_api(test_text, "test_voice_api.wav")