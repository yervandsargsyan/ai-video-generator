import re 
from typing import Literal
from utils.logger import logger
from youtube.uploader import upload_video 
from utils.dir_handler import clean_assets
from config import config


def final_upload(upload: bool,
             topic: str,
             text: str,
             video_path: str,
             visibility: Literal["public", "private", "unlisted"] = config.uploader.privacy_status,
             thumbnail_path: str = None,
             clean_after: bool = False) -> str:
    if upload:
        try:
            logger.info("Uploading video to YouTube...")
            
            # title safe
            safe_title = re.sub(r'[<>\"\'&]', '', topic.strip())
            if len(safe_title) > config.text.max_title_length:
                safe_title = safe_title[:config.text.max_title_length] + "..."

            # description safe
            if len(text) < config.text.max_description_length:
                safe_description = text 
            else:
                safe_description = text[:config.text.max_description_length] + "..."

            # tags safe
            tag_words = re.findall(r'\w+', safe_title)
            safe_tags = list(dict.fromkeys(tag_words[:config.text.max_tags])) # unique tags with limit
            safe_tags.append("shorts") # add topic as tag
            
            upload_video(
                file_path = video_path,
                title = safe_title,
                description = safe_description,
                tags = safe_tags,
                privacy_status = visibility,
                thumbnail_path = thumbnail_path
            )

            logger.info("Video uploaded successfully")

            #  Clean local files
            if clean_after:
                clean_assets()

        except Exception as e:
            logger.error(f"Error per uploading: {e}")
            logger.info("Local files was not deleted")
    