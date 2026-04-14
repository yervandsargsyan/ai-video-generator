import wave
import soundfile as sf
import numpy as np
from scipy.signal import resample
from config import config

def make_voice_more_natural_inplace(audio_path: str, 
                                    speed: float = config.audio.voice_speed, 
                                    fade_ms: int = config.audio.voice_fade_ms) -> str:
    """
    More natural TTS
    """
    # Reading WAV
    audio, sr = sf.read(audio_path)
    
    # Resampling
    num_samples = int(len(audio) / speed)
    audio_slowed = resample(audio, num_samples)
    
    # fade-in/fade-out
    fade_samples = int(sr * fade_ms / 1000) # to sec
    if fade_samples > 0:
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        audio_slowed[:fade_samples] *= fade_in
        audio_slowed[-fade_samples:] *= fade_out
    
    # Rewriting (same file)
    sf.write(audio_path, audio_slowed, sr)
    
    return audio_path


def add_background_music(voice_path: str, 
                         music_path: str, 
                         output_path: str = None, 
                         music_volume: float = config.audio.music_volume) -> str:
    """
    add background music
    """
    # --- Load voice ---
    if not output_path:
        output_path = voice_path

    with wave.open(voice_path, 'rb') as wf:
        params = wf.getparams()
        voice = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        voice_len = len(voice)

    # --- Load music ---
    with wave.open(music_path, 'rb') as wf:
        music = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        if len(music) >= voice_len:
            music = music[:voice_len]
        else:
            repeats = voice_len // len(music) + 1
            music = np.tile(music, repeats)[:voice_len]

    # --- Mix ---
    combined_float = voice.astype(np.float32) + music.astype(np.float32) * music_volume
    combined_float = np.clip(combined_float, -32768, 32767) # range for int16
    combined = combined_float.astype(np.int16)

    # --- Save ---
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(1)  # mono
        wf.setsampwidth(params.sampwidth)
        wf.setframerate(params.framerate)
        wf.writeframes(combined.tobytes())

    return output_path

# Test
if __name__ == "__main__":
    voice_file = config.path.test_audio_path
    music_file = config.path.background_music_path
    final_audio = add_background_music(voice_file, music_file)
    print(f"Final audio file: {final_audio}")