"""Cohere Chat V2 integration."""
from .common import PROMPT, verify

def generate(key, model):
 import cohere
 import httpx
 with httpx.Client(timeout=30) as transport:
  client = cohere.ClientV2(api_key=key, timeout=30, httpx_client=transport)
  response = client.chat(model=model, messages=[{"role":"user", "content":PROMPT}], max_tokens=256, request_options={"max_retries":0})
  return "".join(part.text for part in response.message.content or [] if getattr(part, "text", None))


def test_provider():
 return verify("Cohere", generate)
