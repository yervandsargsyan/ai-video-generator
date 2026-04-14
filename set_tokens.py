from dotenv import load_dotenv
import os

load_dotenv()

replicate_token = os.getenv("REPLICATE_API_TOKEN")
grok_token = os.getenv("GROQ_API_KEY")

print("Replicate token:", replicate_token)
print("Grok token:", grok_token)