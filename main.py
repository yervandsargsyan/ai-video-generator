from typing import Optional, List, Literal
from utils.dir_handler import ensure_directories
from utils.logger import logger
from config import config

from pipeline.topic import prepare_topic
from pipeline.text import prepare_text
from pipeline.audio import prepare_audio
from pipeline.scenes import prepare_scenes
from pipeline.images import prepare_images
from pipeline.video import create_video
from pipeline.upload import final_upload

def run_pipeline(topic: Optional[str] = None, 
                 text: Optional[str] = None, 
                 need_text_modify: bool = True,
                 audio_path: Optional[str] = None, 
                 voice_modify_required: bool = True, 
                 need_bg_music: bool = True, 
                 bg_music_path: Optional[str] = config.path.background_music_path,
                 scenes: Optional[List[str]] = None, 
                 images: Optional[List[str]] = None,
                 upload: bool = True,
                 video_path: str = None,
                 visibility: Literal["public", "private", "unlisted"] = config.uploader.privacy_status,
                 thumbnail_path: str = None,
                 clean_after: bool = False) -> None:
    """
    Full video generation pipeline with YouTube upload.

    Args:
        topic: Optional[str] - YouTube video topic; generated if not provided
        text: Optional[str] - Video script; generated from topic if not provided
        need_text_modify: bool - Whether to modify generated text
        audio_path: Optional[str] - Path to audio file; generates TTS if not provided
        voice_modify_required: bool - Enhance voice naturalness
        need_bg_music: bool - Add background music
        bg_music_path: Optional[str] - Path to background music
        scenes: Optional[List[str]] - List of scene descriptions
        images: Optional[List[str]] - Pre-generated images
        upload: bool - Upload to YouTube if True
        visibility: Literal["public", "unlisted"] - Video privacy
        thumbnail_path: Optional[str] - Path to thumbnail
        clean_after: bool - Delete local assets after upload
    """
    
    logger.info("Starting AI-YouTube pipeline")

    # Autogenerate topic
    topic = prepare_topic(topic = topic)

    # Autogenerate scenes
    text = prepare_text(text = text,
                        topic = topic, 
                        need_text_modify = need_text_modify)

    # Text to speech
    audio_path = prepare_audio(audio_path = audio_path,
                                text = text,  
                                voice_modify_required = voice_modify_required, 
                                need_bg_music = need_bg_music, 
                                bg_music_path = bg_music_path)

    # Generate scenes
    scenes = prepare_scenes(scenes = scenes, text = text)

    # Generate images 
    images = prepare_images(images = images,
                                  scenes = scenes)

   # Create video
    video_path = create_video(images = images, 
                              audio_path = audio_path,
                              script = text)

    # Upload to YouTube
    final_upload(upload = upload,
                 topic = topic, 
                 text = text,
                 video_path = video_path, 
                 visibility=visibility, 
                 thumbnail_path=thumbnail_path, 
                 clean_after=clean_after)



def main(topic = None) -> None:

    ensure_directories()
    run_pipeline()


if __name__ == "__main__":
    main()