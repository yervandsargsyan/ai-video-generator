from __future__ import annotations
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from config import config
from utils.logger import logger


def get_youtube_service() -> any:
    """getting youtube uploader builder"""

    credentials = None
    if os.path.exists(config.uploader.token_file):
        credentials = Credentials.from_authorized_user_file(config.uploader.token_file, [config.uploader.scopes])

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.uploader.client_secrets_file, [config.uploader.scopes])
            credentials = flow.run_local_server(port=0)
        with open(config.uploader.token_file, "w") as token:
            token.write(credentials.to_json())

    youtube = build(config.uploader.api_service_name, config.uploader.api_version, credentials=credentials)
    return youtube


def upload_video(
    file_path: str,
    title: str,
    description: str = "",
    tags: list[str] = None,
    category_id: str = config.uploader.category,
    privacy_status: str = config.uploader.privacy_status,
    thumbnail_path: str = None
) -> dict:
    """Loading video + official preview for YouTube"""

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Can't find video: {file_path}")

    youtube = get_youtube_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status,
            "embeddable": True
        }
    }

    file_size = os.path.getsize(file_path)
    logger.info(f"Video size: {file_size / (1024**2):.2f} MB")

    media = MediaFileUpload(file_path, chunksize = 10 * 1024 * 1024, resumable = True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    retry_count = 0
    max_retries = config.uploader.max_retries

    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Loading: {int(status.progress() * 100)}%")
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                logger.error(f"Loading error (by retry limit): {e}")
                raise
            logger.warning(f"Loading error (attemp {retry_count}/{max_retries}): {e}")

    video_id = response.get("id")
    logger.info(f"Video uploaded succesfully. ID: {video_id}")
    logger.info(f"Link: https://www.youtube.com/watch?v={video_id}")

    # Auto-preview
    if thumbnail_path and os.path.exists(thumbnail_path):
        media_thumb = MediaFileUpload(thumbnail_path)
        youtube.thumbnails().set(videoId=video_id, media_body=media_thumb).execute()

    return response


if __name__ == "__main__":
    video_path = config.path.test_video_path
    thumbnail_path = config.path.test_image_path
    title = "Title"
    description = "Descripton"
    tags = ["tag1", "tag2", "tag3"]
    
    try:
        upload_video(
            file_path = video_path,
            title = title,
            description = description,
            tags = tags,
            privacy_status = config.uploader.test_privacy_status,
            thumbnail_path=config.path.test_image_path
        )
    except Exception as e:
        logger.error(f"Ошибка: {e}")