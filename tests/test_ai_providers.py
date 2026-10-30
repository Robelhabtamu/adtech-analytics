from types import SimpleNamespace as NS
from unittest.mock import Mock
import httpx
import pytest
from adtech_analytics.ai import common, gemini, cohere, groq
from scripts import verify_apis as verification

MODULES = [gemini, cohere, groq]

@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
 for provider in common.DEFAULTS:
  monkeypatch.delenv(provider.upper() + "_API_KEY", raising=False)
  monkeypatch.delenv(provider.upper() + "_MODEL", raising=False)

@pytest.mark.parametrize("module", MODULES)
def test_missing(module, monkeypatch):
 generate = Mock()
 monkeypatch.setattr(module, "generate", generate)
 assert module.test_provider().status == "MISSING_KEY"
 generate.assert_not_called()

@pytest.mark.parametrize("module", MODULES)
@pytest.mark.parametrize("code,status", [(401,"AUTHENTICATION_ERROR"),(403,"ACCESS_RESTRICTED"),(404,"MODEL_UNAVAILABLE"),(429,"RATE_LIMITED"),(500,"FAILED")])
def test_errors(module, code, status, monkeypatch):
 exc = Exception("secret must never escape")
 exc.status_code = code
 monkeypatch.setenv(module.__name__.split(".")[-1].split("_")[0].upper()+"_API_KEY", "secret")
 monkeypatch.setattr(module,"generate",Mock(side_effect=exc))
 result = module.test_provider()
 assert result.status == status
 assert "secret" not in result.message

@pytest.mark.parametrize("module", MODULES)
@pytest.mark.parametrize("value,status", [("CTR is clicks divided by impressions.","SUCCESS"),("", "FAILED"),("  ","FAILED"),(None,"FAILED")])
def test_response(module,value,status,monkeypatch):
 monkeypatch.setenv(module.__name__.split(".")[-1].split("_")[0].upper()+"_API_KEY", "secret")
 monkeypatch.setattr(module,"generate",Mock(return_value=value))
 assert module.test_provider().status == status

@pytest.mark.parametrize("module", MODULES)
def test_timeout(module,monkeypatch):
 monkeypatch.setenv(module.__name__.split(".")[-1].split("_")[0].upper()+"_API_KEY", "secret")
 monkeypatch.setattr(module,"generate",Mock(side_effect=httpx.ReadTimeout("secret")))
 assert module.test_provider().status == "NETWORK_ERROR"

def test_independent(monkeypatch):
 checks = [Mock(return_value=NS(status=s)) for s in ["FAILED","SUCCESS","SUCCESS"]]
 monkeypatch.setattr(verification,"PROVIDERS",dict(zip(["gemini","cohere","groq"],checks)))
 assert [r.status for r in verification.run_all()] == ["FAILED","SUCCESS","SUCCESS"]
 for check in checks:
  check.assert_called_once()

def test_sdk_adapters(monkeypatch):
 from google import genai
 import cohere as cohere_sdk
 import groq as groq_sdk
 google_client = Mock()
 google_client.__enter__ = Mock(return_value=google_client)
 google_client.__exit__ = Mock(return_value=False)
 google_client.models.generate_content.return_value = NS(text="CTR text")
 monkeypatch.setattr(genai,"Client",Mock(return_value=google_client))
 assert gemini.generate("secret","model") == "CTR text"
 co = Mock()
 co.chat.return_value = NS(message=NS(content=[NS(text="CTR text")]))
 monkeypatch.setattr(cohere_sdk,"ClientV2",Mock(return_value=co))
 assert cohere.generate("secret","model") == "CTR text"
 gr = Mock()
 gr.__enter__ = Mock(return_value=gr)
 gr.__exit__ = Mock(return_value=False)
 gr.chat.completions.create.return_value = NS(choices=[NS(message=NS(content="CTR text"))])
 monkeypatch.setattr(groq_sdk,"Groq",Mock(return_value=gr))
 assert groq.generate("secret","model") == "CTR text"
 for call in [google_client.models.generate_content.call_args, co.chat.call_args, gr.chat.completions.create.call_args]:
  assert common.PROMPT in str(call)

def test_reports_and_exit(monkeypatch,tmp_path):
 monkeypatch.setattr(verification,"ROOT",tmp_path)

 monkeypatch.setattr(verification,"load_environment",lambda:None)
 assert verification.main() == 1
 text = (tmp_path / "data/processed/api-verification.json").read_text()
 assert "MISSING_KEY" in text
 assert "api_key_configured" in text


def test_gemini_content_api_options(monkeypatch):
 from google import genai
 client = Mock()
 client.__enter__ = Mock(return_value=client)
 client.__exit__ = Mock(return_value=False)
 client.models.generate_content.return_value = NS(text="CTR means click-through rate.")
 factory = Mock(return_value=client)
 monkeypatch.setattr(genai,"Client",factory)
 assert gemini.generate("secret","gemini-3.8-flash",prompt="What is CTR in digital advertising?")
 client.models.generate_content.assert_called_once_with(model="gemini-3.8-flash",contents="What is CTR in digital advertising?")
 client.interactions.create.assert_not_called()
 options = factory.call_args.kwargs["http_options"]
 assert options.timeout == 30000
 assert options.retry_options.attempts == 1
