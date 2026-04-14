from typing import Optional, Literal
from utils.logger import logger
from agents.voice_agent import generate_voice, generate_voice_google_api
from utils.audio_handler import make_voice_more_natural_inplace, add_background_music
from config import config


def prepare_audio(audio_path: Optional[str] = None,
                mode: Literal["google_api", "local"] = config.audio.tts_mode,
                text: Optional[str] = None,
                voice_modify_required: bool = True, 
                need_bg_music: bool = True, 
                bg_music_path: Optional[str] = config.path.background_music_path) -> str:
    
    # Generate audio (TTS)
    if not audio_path:
        if mode == "google_api":
            audio_path = generate_voice_google_api(text)
        else:
            audio_path = generate_voice(text)
        logger.info(f"Audio generated: {audio_path}")
    
    # Modify audio
    if voice_modify_required:
        audio_path = make_voice_more_natural_inplace(audio_path, 
                                                     speed = config.audio.voice_speed, 
                                                     fade_ms = config.audio.voice_fade_ms)
        logger.info(f"Audio modified: {audio_path}")
    
    # Add background music
    if need_bg_music:
        if bg_music_path:
            music_path = bg_music_path
            audio_path = add_background_music(audio_path, 
                                              music_path, 
                                              music_volume = config.audio.music_volume)
            logger.info(f"Added background music: {audio_path}")
        else:
            logger.info(f"Enter background music's path")
    
    return audio_path