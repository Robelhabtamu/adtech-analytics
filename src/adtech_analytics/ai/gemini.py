"""Google's official Gen AI SDK."""
from .common import PROMPT, verify

def generate(key, model, prompt=PROMPT):
 from google import genai
 from google.genai import types
 with genai.Client(api_key=key, http_options=types.HttpOptions(timeout=30000, retry_options=types.HttpRetryOptions(attempts=1))) as client:
  response = client.models.generate_content(model=model, contents=prompt)
  return response.text

def test_provider():
 return verify("Gemini", generate)
