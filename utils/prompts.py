
def topic_prompt(cache_text: str, lang: str = "ru") -> str:
    """
    topic_prompt generates a prompt for the topic generation agent. 
    It includes recently used topics from the cache to avoid repetition 
    and encourages the model to create a unique topic. 
    The final output is translated to the specified language.
    
    Note1: Ensure that the cache_text variable is properly 
    formatted with recent topics before using this prompt.
    
    Note2: The prompt instructs the model to return only the final translated topic, 
    without any additional text or explanations.
    
    Note3: The lang parameter allows you to specify the language for the generated topic, 
    ensuring that the output is in the desired language. 
    In default, it is set to Russian ("ru"), 
    but you can change it to any language supported by the model. 
    
    Local voice generation may not support only russian language, 
    so for other languages it's recommended to use "google_api" TTS mode in config.
    """

    return f"""
# enter a prompt to generate a video topic 
# based on the following recently used topics.

USED TOPICS:
{cache_text}

FINAL STEP:
Translate the result to language: {lang}
Return ONLY the final translated topic.
"""

def script_prompt(topic: str, lang: str = "ru") -> str:
    return f"""
# enter a prompt to generate a script based on the following topic.


TOPIC:
{topic}

FINAL STEP:
Translate entire output to language: {lang}
Return ONLY final result.
"""

def modify_script_prompt(script: str, topic: str, lang: str = "ru") -> str:
    return f"""
# enter a prompt to modify the script for better engagement and retention, 
# based on the following rules and the original script.

INPUT SCRIPT:
{script}

TOPIC:
{topic}

FINAL STEP:
Translate entire output to language: {lang}
Return ONLY final result.
"""

def scene_prompt(script: str) -> str:
    return f"""
    # enter a prompt to break down the script into scenes for image generation,
    # based on the following rules and the original script.

    SCRIPT:
    {script}

    Return only 12-15 scenes line by line.
    """