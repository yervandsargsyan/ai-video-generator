from typing import Optional
from utils.logger import logger
from agents.script_agent import generate_script, modify_script
from config import config

def prepare_text(text: Optional[str] = None, 
                topic: Optional[str] = None,  
                need_text_modify: bool = True) -> str:
    
    if not text and not topic:
        raise ValueError("You must provide either non-empty 'text' or 'topic'")
    # Using default
    if text:
        logger.info("Using manual text")
        logger.debug(f"\n=== MANUAL TEXT ===\n{text}\n=== END ===")
        return text

    # Generate text
    text = generate_script(topic, config.text.generate_script_retries)
    logger.info("Text generated")
    logger.debug(f"\n=== GENERATED TEXT ===\n{text}\n=== END ===")

    # Modify text
    if need_text_modify:
        text = modify_script(text, topic, config.text.modify_script_retries)
        logger.info("Text modified")
        logger.debug(f"\n=== MODIFIED TEXT ===\n{text}\n=== END ===")

    return text
    