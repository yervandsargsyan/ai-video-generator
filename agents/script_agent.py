from __future__ import annotations
import time
from agents.api_loader import load_groq
from utils.prompts import script_prompt, modify_script_prompt
from utils.logger import logger
from config import config

client = load_groq()


def generate_script(topic: str, retries: int = config.text.generate_script_retries) -> str:
    """Generates a script for video on a specific topic."""
    prompt = script_prompt(topic)
    
    attempt = 0
    while attempt < retries:
        try:
            completion = client.chat.completions.create(
                model=config.models.script_agent_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.models.script_agent_temperature,
                max_tokens=config.models.script_agent_max_tokens
            )

            text = completion.choices[0].message.content.strip()

            if text and len(text) > config.text.min_text_length:
                logger.info(f"The script has been successfully generated on the topic '{topic}'")
                return text

            attempt += 1
            logger.warning(f"Groq API returned text that was too short: retry {attempt}/{retries}")
            time.sleep(2)

        except Exception as e:
            logger.error(f"Error per script generation: {e}")
            attempt += 1
            time.sleep(2)

    raise RuntimeError("Unable to retrieve the full text from the Groq API after several attempts")

def modify_script(script: str, topic: str, retries: int = config.text.modify_script_retries) -> str:
    """Improves the script without cutting it."""

    prompt = modify_script_prompt(script, topic)

    attempt = 0
    while attempt < retries:
        try:
            completion = client.chat.completions.create(
                model=config.models.script_modify_model,
                messages=[
                    {"role": "system", "content": "Ты редактор сценариев для YouTube Shorts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.models.script_modify_temperature,
                max_tokens=config.models.script_modify_max_tokens
            )

            modified_text = completion.choices[0].message.content.strip()
            word_count = len(modified_text.split())
            logger.info(f"The editor returned {word_count} words")

            if modified_text and word_count >= config.text.min_text_length:
                logger.info("The script has been successfully edited")
                return modified_text

            attempt += 1
            logger.warning(f"The Groq API returned text that was too short ({word_count} words); retry {attempt}/{retries}")
            time.sleep(2)

        except Exception as e:
            logger.error(f"Error per script editing: {e}")
            attempt += 1
            time.sleep(2)

    raise RuntimeError("Unable to retrieve the full text from the Groq API after several attempts")

# Test run
if __name__ == "__main__":
    topic_test = "Что, если ты Сократ, а скелет открыл ЗАВОД в Древней Греции?"

    try:
        script = generate_script(topic_test)
        print("\n=== FULL SCRIPT ===\n")
        print(script)
        print("\n=== END OF SCRIPT ===")
    except Exception as e:
        print(f"error per script creation: {e}")

    try:
        script = modify_script(script, topic_test)
        print("\n=== FULL SCRIPT ===\n")
        print(script)
        print("\n=== END OF SCRIPT ===")
    except Exception as e:
        print(f"error per script creation: {e}")