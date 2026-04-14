from config import config

# load topic cache
def load_topics():
    with open(config.path.cache_file, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f.readlines() if line.strip()]

    return topics

# update cache FIFO
def update_cache(topic: str):
    if topic:
        topics = load_topics()

        # adding new topic
        topics.append(topic)

        # pop old topic from cache
        if len(topics) > config.cache.cahce_size:
            topics.pop(0)

        with open(config.path.cache_file, "w", encoding="utf-8") as f:
            for t in topics:
                f.write(t + "\n")