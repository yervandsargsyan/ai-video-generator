import sys 
import cv2
import re 
import numpy as np
from pathlib import Path
from moviepy.video.VideoClip import VideoClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from PIL import Image, ImageDraw, ImageFont
from utils.logger import logger
from config import config

WIDTH = 1080
HEIGHT = 1920
FPS = 24
TRANSITION = 0.5

def resize_and_crop_image(img_path, width, height):
    """Image scaling and cutting"""
    img = Image.open(img_path)
    img_ratio = img.width / img.height
    target_ratio = width / height

    if img_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    else:
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop((0, top, img.width, top + new_height))

    img = img.resize((width, height), Image.Resampling.LANCZOS)
    return np.array(img, dtype=np.uint8)


def create_zoom_clip(img_array, duration, width, height, 
                     zoom_start=config.video.zoom_start, 
                     zoom_end=config.video.zoom_end):
    """Creates clip with zoom effect"""
    h, w = img_array.shape[:2]
    center_x, center_y = w // 2, h // 2
    
    def make_frame(t):
        zoom = zoom_start + (zoom_end - zoom_start) * (t / duration)
        new_w = max(1, int(w / zoom))
        new_h = max(1, int(h / zoom))
        
        x1 = max(0, center_x - new_w // 2)
        y1 = max(0, center_y - new_h // 2)
        x2 = min(w, x1 + new_w)
        y2 = min(h, y1 + new_h)
        
        cropped = img_array[y1:y2, x1:x2]
        bgr = cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR)
        resized_bgr = cv2.resize(bgr, (width, height), interpolation=cv2.INTER_LINEAR)
        resized = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2RGB)
        
        return resized
    
    return VideoClip(make_frame, duration=duration)


def create_modern_subtitle_frame(width, height, text, font_size, 
                                 padding = config.video.padding, 
                                 line_spacing = config.video.line_spacing):
    """Generates subtitles"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Loading font
    try:
        font = ImageFont.truetype(config.path.subtitle_font_path, font_size)
    except Exception:
        # Defining fallback
        if sys.platform.startswith("win"):
            fallback_path = config.path.fallback_font_path_win
        elif sys.platform.startswith("darwin"):
            fallback_path = config.path.fallback_font_path_mac
        else:
            fallback_path = config.path.fallback_font_path_linux

        # Trying to load fallback
        try:
            font = ImageFont.truetype(fallback_path, font_size)
        except Exception:
            # PIL by default
            font = ImageFont.load_default()
    

    # Split text to words
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = (current_line + " " + word).strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width + 2*padding <= width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Count height
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
    total_text_height = sum(line_heights) + (len(lines) - 1) * line_spacing

    # Start position
    y = height - total_text_height - 250

    # Drawing lines
    for line, lh in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2

        # Outline
        outline_width = 4
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text(
                        (x + adj_x, y + adj_y),
                        line,
                        font=font,
                        fill=(255, 255, 255, 255)
                    )

        # Filling
        draw.text((x, y), line, font=font, fill="white", stroke_width=2, stroke_fill="black")

        y += lh + line_spacing

    return np.array(img, dtype=np.uint8)


def split_text_by_words(text, words_per_chunk=5):
    """
    Splits the text into chunks based on a specified number of words.
    
    text: source text
    words_per_chunk: the number of words in each chunk (default: 5)
    """
    # Text to words
    words = re.findall(r'\S+', text)
    
    chunks = []
    for i in range(0, len(words), words_per_chunk):
        chunk = " ".join(words[i:i+words_per_chunk])
        chunks.append(chunk)
    
    return chunks


def get_optimal_font_size(text, width, height, max_font_size=120):
    try:
        font_path = "C:/Windows/Fonts/arialbd.ttf"
    except:
        font_path = "C:/Windows/Fonts/Arial.ttf"
    
    for font_size in range(max_font_size, 30, -5):
        try:
            font = ImageFont.truetype(font_path, font_size)
            img = Image.new('RGBA', (1, 1))
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Оставляем отступы 60px с каждой стороны
            if text_width < width - 120:
                return font_size
        except:
            continue
    
    return 50


def create_video(images, audio_path, script, output_path="assets/videos/output.mp4", video_path = None):
    if video_path:
        return video_path
    
    if not images:
        raise ValueError("No images")

    Path(Path(output_path).parent).mkdir(parents=True, exist_ok=True)

    logger.info("Loading audio...")
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration
    duration_per_image = total_duration / len(images)
    logger.info(f"Audio duration: {total_duration:.2f} sec, every scene: {duration_per_image:.2f} sec")

    clips = []
    for i, img_path in enumerate(images):
        logger.info(f"Image handling: {i+1}/{len(images)}")
        img_array = resize_and_crop_image(img_path, WIDTH, HEIGHT)
        clip = create_zoom_clip(img_array, duration_per_image, WIDTH, HEIGHT)
        clips.append(clip)

    logger.info("Making final clip...")
    
    final_clips = []
    current_time = 0
    
    for i, clip in enumerate(clips):
        if i == 0:
            final_clips.append(clip.with_start(0))
            current_time = clip.duration - TRANSITION
        else:
            final_clips.append(clip.with_start(current_time))
            current_time += clip.duration - TRANSITION

    extra_last = 5  # sec
    last_clip_index = len(clips) - 1
    final_clips[last_clip_index] = final_clips[last_clip_index].with_duration(
        final_clips[last_clip_index].duration + extra_last
    )    
    logger.info("Adding subtitles...")
    
    phrases = split_text_by_words(script, 5)
    
    time_per_phrase = total_duration / len(phrases)
    
    pause_duration = 0.1
    
    overlay_clips = []
    n = len(phrases)
    total_pause = pause_duration * (n - 1)
    time_per_phrase = (total_duration - total_pause) / n

    for i, phrase in enumerate(phrases):
        phrase_start = i * (time_per_phrase + pause_duration)
        phrase_end = phrase_start + time_per_phrase

        
        if phrase_start >= total_duration:
            logger.warning(f"The phrase {i+1} goes beyond the video frame: skipping")
            break
        
        if phrase_end > total_duration:
            phrase_end = total_duration
        
        duration = phrase_end - phrase_start
        if duration <= 0:
            continue
        
        font_size = get_optimal_font_size(phrase, WIDTH, HEIGHT)
        
        def make_subtitle_frame(t, phrase_text=phrase, font_sz=font_size):
            return create_modern_subtitle_frame(WIDTH, HEIGHT, phrase_text, font_sz)
        
        subtitle_clip = VideoClip(make_subtitle_frame, duration=duration)
        subtitle_clip = subtitle_clip.with_start(phrase_start)
        overlay_clips.append(subtitle_clip)
        
        logger.info(f"Phrase {i+1}: '{phrase}' (Font: {font_size}px, {phrase_start:.2f}s - {phrase_end:.2f}s)")
    
    final_clips.extend(overlay_clips)
    
    video = CompositeVideoClip(final_clips, size=(WIDTH, HEIGHT))
    video = video.with_duration(total_duration)
    video = video.with_audio(audio_clip)

    logger.info("Rendering video...")
    video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=FPS,
        preset="ultrafast",
        threads=8
    )
    logger.info(f"Video created: {output_path}")
    video.close()
    audio_clip.close()
    return output_path


if __name__ == "__main__":
    test_images = [
        r'assets\images\scene_01.png',
        r'assets\images\scene_02.png',
        r'assets\images\scene_03.png'
    ]
    test_audio = r"assets\audio\voice.wav"
    subtitle_words = "Subtitles for text"
    test_script = ""
    for _ in range(20):
        test_script += subtitle_words
        test_script+=" "

    create_video(test_images, test_audio, test_script)