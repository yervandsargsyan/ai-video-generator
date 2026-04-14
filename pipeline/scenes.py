from typing import Optional, List
from utils.logger import logger
from agents.scene_agent import generate_scenes

def prepare_scenes(scenes: Optional[List[str]] = None,
                text: Optional[str] = None) -> List[str]:
    
    if scenes:
        logger.info("Using provided scenes")
        return scenes
    
    if not text :
        raise ValueError("You must provide non-empty 'text'")

    scenes = generate_scenes(text)
    logger.info(f"{len(scenes)} scenes generated")
    return scenes