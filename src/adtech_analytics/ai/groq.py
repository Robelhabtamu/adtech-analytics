"""Groq's official chat completion SDK."""
from .common import PROMPT, verify

def generate(key, model):
 from groq import Groq
 with Groq(api_key=key, timeout=30, max_retries=0) as client:
  response = client.chat.completions.create(model=model, messages=[{"role":"user", "content":PROMPT}], max_completion_tokens=1024)
  return response.choices[0].message.content

def test_provider():
 return verify("Groq", generate)
