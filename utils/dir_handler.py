from pathlib import Path
import shutil
from utils.logger import logger
from config import config

def ensure_directories() -> None:
    """
    Ensure all required asset directories exist.
    """
    dirs = [config.path.audio_dir, config.path.image_dir, config.path.video_dir]

    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)


def clean_assets() -> None:
    """
    Delete all generated files after uploading
    """
    dirs = [config.path.audio_dir, config.path.image_dir, config.path.video_dir]
    for directory in dirs:
        dir_path = Path(directory)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            logger.info(f"Deleted files {directory}")