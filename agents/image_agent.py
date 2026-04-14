from pathlib import Path
from typing import List
import time
import replicate
from PIL import Image
from utils.logger import logger
from config import config
from agents.api_loader import load_replicate

load_replicate()  # Ensure Replicate is loaded at startup  

def generate_images_from_scenes(
    scenes: List[str],
    output_dir: str = config.path.image_dir,
    max_retries: int = config.images.image_generation_max_retries,
    retry_wait: int = config.images.image_generation_retry_wait
) -> List[str]:
    """
    Image generation for scenes with Replicate/Flux-Schnell
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    image_paths = []

    for idx, scene in enumerate(scenes, start=1):
        logger.info(f"Generation of scene {idx}: {scene}")

        for attempt in range(1, max_retries + 1):
            try:
                # Replicate generation
                output_files = replicate.run(
                    config.models.image_generation_model,
                    input={
                        "prompt": scene,
                        "num_outputs": 1,
                        "aspect_ratio": config.images.image_aspect_ratio,
                        "output_format": config.images.image_output_format,
                        "output_quality": config.images.image_output_quality,
                        "num_inference_steps": config.images.image_num_inference_steps
                    }
                )

                image_path_from_replicate = output_files[0]

                # Local saving
                image = Image.open(image_path_from_replicate)
                image_path = Path(output_dir) / f"scene_{idx:02}.png"
                image.save(image_path)
                logger.info(f"Saved: {image_path}")
                image_paths.append(str(image_path))
                time.sleep(10)
                break  

            except replicate.exceptions.ReplicateError as e:
                logger.warning(f"Error per generation scene {idx}, attemp {attempt}/{max_retries}: {e}")
                time.sleep(retry_wait)

            except Exception as e:
                logger.error(f"Unexpected error for scene {idx}: {e}")
                time.sleep(retry_wait)

        else:
            logger.error(f"Scene {idx} was not generated after {max_retries} attemps!")

    return image_paths


if __name__ == "__main__":
    # Test scenes
    scenes = [
        "The King of Babylon watches as the ancient city becomes the center of the region"
    ]

    image_paths = generate_images_from_scenes(scenes)

    logger.info("Images generated succesfully!")
    for path in image_paths:
        logger.info(f"Generated image: {path}")