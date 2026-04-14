from __future__ import annotations
import time
from agents.api_loader import load_groq
from utils.logger import logger
from utils.prompts import scene_prompt
from config import config

client = load_groq()

# Generate scenes

def generate_scenes(script: str, retries: int = config.text.generate_scene_retries) -> list[str]:
    """
    Breaks the script down into scenes for image generation
    """

    prompt = scene_prompt(script)

    attempt = 0

    while attempt < retries:
        try:

            completion = client.chat.completions.create(
                model=config.models.scene_agent_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.models.scene_agent_temperature,
                max_tokens=config.models.scene_agent_max_tokens
            )

            text = completion.choices[0].message.content.strip()

            if not text:
                raise ValueError("Empty answer from model")


            scenes = []

            for line in text.split("\n"):

                line = line.strip()

                if not line:
                    continue

                # remove numerating
                if line[0].isdigit():
                    line = line.split(".", 1)[1].strip()

                # добавляем единый стиль
                scene = f"{line}, cinematic lighting, ultra realistic, 8k"

                scenes.append(scene)

            logger.info(f"Created {len(scenes)} scenes")
            if len(scenes) > config.text.max_scene_number:
                scenes = scenes[:config.text.max_scene_number]
            return scenes

        except Exception as e:

            attempt += 1
            logger.error(f"Error per generating scenes: {e}")
            time.sleep(2)

    raise RuntimeError("Unable to generate scenes")


# Test
if __name__ == "__main__":

    script_test = """
A galaxy is a huge collection of gas, dust, 
and billions of stars and their solar systems, all held together by gravity.
We live on a planet called Earth that is part of our solar system. 
But where is our solar system? Its a small part of the Milky Way Galaxy.
"""

    scenes = generate_scenes(script_test, "Galaxy")

    print("\n=== SCENES ===\n")

    for i, scene in enumerate(scenes):
        print(f"{i+1}. {scene}")

    print("\n=== END ===")