# topic_agent.py

from __future__ import annotations
import time
from agents.api_loader import load_groq
from utils.topic_handler import load_topics, update_cache
from utils.prompts import topic_prompt
from utils.logger import logger
from config import config

client = load_groq()


def generate_topic(retries: int = config.text.generate_topic_retires):
    """
    Generates a unique topic for YouTube Shorts.
    Uses an LLM to ensure the topic is complete,
    unique, and begins with “What if you...”.
    """
    attempt = 0

    while attempt < retries:
        try:
            # loading cached themes
            cache = load_topics()
            cache_text = "\n".join(cache)

            prompt = topic_prompt(cache_text)

            completion = client.chat.completions.create(
                model = config.models.topic_agent_model,
                messages = [{"role": "user", "content": prompt}],
                temperature = config.models.topic_agent_temperature,
                max_tokens = config.models.topic_agent_max_tokens
            )

            topic = completion.choices[0].message.content
            if topic is None:
                attempt += 1
                continue

            topic = topic.strip()
            words = topic.split()

            # checking length
            if len(words) < config.text.min_topic_length:
                logger.info(f"Topic too short, retrying: {topic}")
                attempt += 1
                continue

            # Check for truncated words
            if topic[-1] in {"…", "-", ","} or len(words[-1]) <= 2:
                logger.info(f"Topic truncated, retrying: {topic}")
                attempt += 1
                continue

            # Check for theme start
            if not topic.lower().startswith("что если"):
                logger.info(f"Topic does not start with 'что если', retrying: {topic}")
                attempt += 1
                continue

            # Check for unity
            if topic in cache:
                logger.info(f"The LLM repeated the topic: {topic}")
                attempt += 1
                continue

            # Ok - updating cache
            update_cache(topic)
            return topic

        except Exception as e:
            logger.error(f"Error per theme generation: {e}")
            attempt += 1
            time.sleep(2)

    raise RuntimeError("Unable to retrieve the topic after several attempts")


# ==============================
# Test
# ==============================
if __name__ == "__main__":
    try:
        topic = generate_topic()
        print(topic)
    except Exception as e:
        print(f"Error per theme generation: {e}")