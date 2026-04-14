from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class AudioConfig:
    voice_speed: float = 1.0
    voice_fade_ms: int = 10
    music_volume: float = 0.6 # background music volume
    sample_rate_local: int = 48000
    sample_rate_api: int = 24000
    pause_sample_rate: int = 24000
    pause_duration: float = 0.2 # duration of pause between audio segments in seconds
    tts_chunk_size: int = 120 # number of characters in each TTS chunk
    tts_language: str = 'ru' # in fact only ru supported for local tts, wait for updates for more languages support, but you can use google tts for other languages
    tts_model: str = 'silero_tts'
    tts_model_id: str = 'v5_cis_base_nostress'
    tts_speaker: str = 'ru_miyau'
    tts_mode: Literal["google_api", "local"] = "local" # "google_api" or "local" ensure you entered GOOGLE_TTS_API_KEY in .env if you choose "google_api"
    google_tts_voice: str = "ru-RU-Chirp3-HD-Charon" # only for google tts, see available voices here: https://cloud.google.com/text-to-speech/docs/voices 
    google_tts_language_code: str = "ru-RU" # google tts language code

@dataclass(frozen=True)
class ImageConfig:
    image_aspect_ratio: str = "9:16"
    image_output_format: str = "png"
    image_output_quality: int = 100
    image_num_inference_steps: int = 4
    image_generation_max_retries: int = 3
    image_generation_retry_wait: int = 10


@dataclass(frozen=True)
class TextConfig:
    max_title_length: int = 100
    max_description_length: int = 300
    max_tags: int = 10
    summary_sentences: int = 3
    generate_topic_retires: int = 10 # maximum 10 calls to API for generating topic
    generate_script_retries: int = 3 # maximum 3 calls to API for generating script
    modify_script_retries: int = 5 #  maximum 5 calls to API for modifying script 
    generate_scene_retries: int = 3 # maximum 3 calls to API for generating scenes
    font_color = (218, 165, 32, 255) # subtitle color
    min_topic_length: int = 5 # minimum number of words in topic
    min_text_length: int = 80 # minimum number of characters in generated text
    max_scene_number: int = 15 # maximum number of scenes to generate
    
@dataclass(frozen=True)
class ModelConfig:
    # topic agent parameters
    topic_agent_model: str = "openai/gpt-oss-120b"
    topic_agent_temperature: float = 0.5
    topic_agent_max_tokens: int = 1500

    # scene agent parameters
    scene_agent_model: str = "llama-3.3-70b-versatile"
    scene_agent_temperature: float = 0.7
    scene_agent_max_tokens: int = 1200

    # script agent parameters
    script_agent_model: str = "openai/gpt-oss-120b"
    script_agent_temperature: float = 0.7
    script_agent_max_tokens: int = 3000
    script_modify_model: str = "openai/gpt-oss-120b"
    script_modify_temperature: float = 0.5
    script_modify_max_tokens: int = 3500

    # image generation parameters
    image_generation_model: str = "black-forest-labs/flux-schnell"

@dataclass(frozen=True)
class PathConfig:
    # assets dirs
    audio_dir: str = "assets/audio" 
    image_dir = "assets/images" 
    video_dir = "assets/videos"   
    audio_path: str = "assets/audio/voice.wav"
    background_music_path: str = "extras/background_music.wav"
    video_path: str = "assets/videos/output.mp4"
    
    # fonts
    subtitle_font_path: str = "extras/subtitle_font.ttf"
    fallback_font_path_win: str = "C:/Windows/Fonts/Arial.ttf"
    fallback_font_path_mac: str = "/System/Library/Fonts/Supplemental/Arial.ttf"
    fallback_font_path_linux: str = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
     
    # for tests
    test_audio_path: str = "extras/test_audio.wav" 
    test_video_path: str = "extras/test_video.wav"
    test_image_path: str = "extras/test_img.png"

    # other paths
    cache_file: str = "utils/topic_cache.txt"
    siero_model_dir: str = "snakers4/silero-models"


@dataclass(frozen=True)
class UploaderConfig:
    client_secrets_file: str = "client_secrets.json"
    token_file: str = "token.json"
    api_service_name: str = "youtube"
    api_version: str = "v3"
    scopes: str = "https://www.googleapis.com/auth/youtube.upload"
    max_retries: int = 3
    category: str = "27" # info: https://gist.github.com/dgp/1b24bf2961521bd75d6c
    privacy_status: str = "public" # private / public / unlisted
    test_privacy_status = "unlisted" # only for tests


@dataclass(frozen=True)
class CacheConfig:
    cahce_size: int = 10


@dataclass(frozen=True)
class VideoConfig:
    width: int = 1080
    height: int = 1920
    fps: int = 24
    transition: float = 0.5
    zoom_start: float = 1.0
    zoom_end: float = 1.15
    padding: int = 120
    line_spacing: int = 10

@dataclass(frozen=True)
class Config:
    audio: AudioConfig = AudioConfig()
    text: TextConfig = TextConfig()
    path: PathConfig = PathConfig()
    cache: CacheConfig = CacheConfig()
    uploader: UploaderConfig = UploaderConfig()
    video: VideoConfig = VideoConfig()
    models: ModelConfig = ModelConfig()
    images: ImageConfig = ImageConfig()

config = Config()