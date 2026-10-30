"""Shared verification contract; never persist raw exceptions or generated content."""
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

PROMPT = "Explain click-through rate (CTR) in digital advertising in one sentence."
ROOT = Path(__file__).resolve().parents[3]
DEFAULTS = {"Gemini": "gemini-3.5-flash-lite", "Cohere": "command-a-03-2025", "Groq": "openai/gpt-oss-20b"}
MESSAGES = {
 "SUCCESS": "Generated nonempty text.",
 "MISSING_KEY": "Add the provider API key to local .env; see README.md.",
 "AUTHENTICATION_ERROR": "Credentials rejected; check or rotate the local key.",
 "ACCESS_RESTRICTED": "Access denied; check account permissions and provider eligibility. Geography is unconfirmed.",
 "MODEL_UNAVAILABLE": "Model unavailable; check the configured model and account access.",
 "RATE_LIMITED": "Rate or quota limit reached; check provider usage and billing.",
 "NETWORK_ERROR": "Connection failed or timed out; check connectivity and retry manually.",
 "FAILED": "Unexpected error or empty response; check SDK configuration and provider dashboard.",
}
@dataclass
class Result:
 provider: str
 model: str
 api_key_configured: bool
 status: str
 timestamp: str
 message: str

def load_environment():
 from dotenv import load_dotenv
 load_dotenv(ROOT / ".env", override=False)

def classify(exc):
 code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
 if str(code) == "400" and "API_KEY_INVALID" in str(exc):
  return "AUTHENTICATION_ERROR"
 status = {"401":"AUTHENTICATION_ERROR", "403":"ACCESS_RESTRICTED", "404":"MODEL_UNAVAILABLE", "429":"RATE_LIMITED"}.get(str(code))
 if status:
  return status
 # SDK wrappers often carry the underlying httpx error as their cause.
 current = exc
 while current is not None:
  if isinstance(current, (TimeoutError, ConnectionError)) or any(s in type(current).__name__.lower() for s in ("timeout", "connection", "connecterror", "network")):
   return "NETWORK_ERROR"
  current = current.__cause__
 return "FAILED"

def verify(provider, generate):
 key = os.getenv(provider.upper() + "_API_KEY", "").strip()
 model = os.getenv(provider.upper() + "_MODEL", "").strip() or DEFAULTS[provider]
 # Only model identifiers may be written to logs/reports, never arbitrary env values.
 import re
 safe_model = model if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,119}", model) and model != key else "invalid-model-setting"
 status = "MISSING_KEY"
 if key:
  try:
   if safe_model == "invalid-model-setting":
    raise ValueError("Invalid model setting")
   value = generate(key, model)
   status = "SUCCESS" if isinstance(value, str) and value.strip() else "FAILED"
  except Exception as exc:
   status = classify(exc)
 return Result(provider, safe_model, bool(key), status, datetime.now(timezone.utc).isoformat(), MESSAGES[status])
