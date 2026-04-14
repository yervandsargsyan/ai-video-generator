from typing import Optional
from utils.logger import logger
from agents.topic_agent import generate_topic

def prepare_topic(topic: Optional[str] = None) -> str:
    if not topic:
        topic = generate_topic()
        logger.info(f"Topic generated: {topic}")
    else:
        logger.info(f"Using manual topic {topic}")
    return topic