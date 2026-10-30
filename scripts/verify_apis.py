"""Live API checks: all providers by default, or one provider by name."""
import argparse
import json
from dataclasses import asdict

from adtech_analytics.ai import gemini, cohere, groq
from adtech_analytics.ai.common import ROOT, load_environment

PROVIDERS = {
    "gemini": gemini.test_provider,
    "cohere": cohere.test_provider,
    "groq": groq.test_provider,
}


def run_all():
    return [check() for check in PROVIDERS.values()]


def main(provider=None):
    load_environment()
    results = [PROVIDERS[provider]()] if provider else run_all()
    print("AdTech AI Provider Verification\n--------------------------------")
    for result in results:
        print(f"{result.provider}: {result.status}\n"
              f"  Model: {result.model} | UTC: {result.timestamp}\n"
              f"  {result.message}")
    count = sum(result.status == "SUCCESS" for result in results)
    print(f"--------------------------------\nSuccessful providers: {count}/{len(results)}")
    output = ROOT / "data/processed/api-verification.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps([asdict(result) for result in results], indent=2) + "\n", encoding="utf-8")
    return 0 if count == len(results) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider", choices=PROVIDERS, nargs="?")
    raise SystemExit(main(parser.parse_args().provider))
