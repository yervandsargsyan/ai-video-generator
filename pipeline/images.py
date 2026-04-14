from typing import Optional, List
from utils.logger import logger
from agents.image_agent import generate_images_from_scenes

def prepare_images(images: Optional[List[str]] = None,
                   scenes: Optional[List[str]] = None) -> List[str]:
    
    if images:
        logger.info(f"Using {len(images)} default images")
        return images
    
    if not scenes:
        raise ValueError("You must provide non-empty 'scenes'")
    
    images = generate_images_from_scenes(scenes)
    logger.info(f"{len(images)} images generated")
    return images
