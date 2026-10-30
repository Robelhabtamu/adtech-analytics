# AdTech Analytics

A small Python project for an AdTech analytics and AI engineering preparation assignment. It demonstrates pandas-based campaign processing, reusable advertising KPIs, three AI provider integrations, mocked tests and basic CI.

## Structure

```text
.github/workflows/ci.yml          Automated Python tests
data/sample/campaigns.csv        Three synthetic advertising records
notebooks/                      Reserved for exploratory analysis
pipelines/process_sample.py     Load CSV, aggregate campaigns, export KPIs
scripts/verify_apis.py           Live AI verification CLI
src/adtech_analytics/
    analytics.py                Reusable KPI calculations
    ai/                         Gemini, Cohere, Groq and shared error handling
tests/                          KPI and mocked provider tests
.env.example                    Key names and optional model settings
.gitignore                      Secrets and generated-file exclusions
pyproject.toml                  Package and dependency configuration
README.md                       Setup, architecture and verification evidence
```

`__init__.py` files mark the reusable Python packages. Local `.env` and `.venv` are excluded from version control. Generated CSV and verification JSON go to ignored `data/processed/`.

## Architecture and scope

Implemented flow: sample CSV -> pandas campaign aggregation -> KPI calculations -> campaign summary CSV. Counts and spend are summed before computing CTR, CPM, CPC, conversion rate, CPA and ROAS; zero denominators return `None`. The AI CLI independently sends a one-sentence CTR prompt to each provider and validates nonempty text.

Real datasets need explicit grain, currency, units, timezone and attribution definitions before joins; bidding, impression and click logs are not interchangeable. The included data is synthetic. No notebook has been authored yet; `notebooks/` reserves its intended location, and Jupyter is not required to run the project.

Planned flow: cleaned advertising data -> Neon PostgreSQL -> Next.js dashboard on Vercel and automated email summaries. Database integration, dashboard, email transport and scheduling are not implemented. GitHub, Vercel and Neon accounts were configured by the project owner; this does not establish a deployment or database connection.

## Setup

Python 3.11+; run commands from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,providers]"
```

On macOS/Linux activate with `source .venv/bin/activate`. pandas is the core dependency; pytest is the development extra. The providers extra installs python-dotenv and the official google-genai, cohere and groq SDKs. CI installs both extras and runs mocked tests without keys.

## API configuration

If `.env` does not exist, copy `.env.example` to `.env`; otherwise preserve the existing file. Create keys in the provider consoles and edit `.env` locally. Never paste credentials into chat or commit them. Shell environment variables take precedence over `.env`.

| Provider | Registration and API keys | Key variable | Default model |
|---|---|---|---|
| Gemini | [AI Studio](https://aistudio.google.com/) / [keys](https://aistudio.google.com/apikey) | GEMINI_API_KEY | gemini-3.5-flash-lite |
| Cohere | [Dashboard](https://dashboard.cohere.com/) / [keys](https://dashboard.cohere.com/api-keys) | COHERE_API_KEY | command-a-03-2025 |
| Groq | [Console](https://console.groq.com/) / [keys](https://console.groq.com/keys) | GROQ_API_KEY | openai/gpt-oss-20b |

Sign in, complete any eligibility checks, and create an evaluation/development key in the key page. Billing decisions and CAPTCHAs require manual completion. Optional `GEMINI_MODEL`, `COHERE_MODEL` and `GROQ_MODEL` override defaults; no automatic model fallback occurs.

## Run and test

```powershell
python pipelines/process_sample.py
python -m pytest -q
python -m compileall -q src scripts tests
python scripts/verify_apis.py
python scripts/verify_apis.py gemini
python scripts/verify_apis.py cohere
python scripts/verify_apis.py groq
```

The pipeline writes `data/processed/campaign_summary.csv`. Verification prints status, model and UTC timestamp, saves only the selected providers' latest results to `data/processed/api-verification.json`, and exits nonzero if any selected provider fails. It never rewrites this README. SUCCESS requires actual nonempty generated text; it does not assess semantic correctness. Automated tests use mocks, do not load `.env` and consume no API quota.

Requests use 30-second HTTP timeouts and no SDK retries; transport phases may each have their own timeout. Raw server errors, headers and generated content are not logged by verification. The CLI preserves these classifications:

- `MISSING_KEY`: no request made; add the local key (NOT TESTED).
- `AUTHENTICATION_ERROR`: check or rotate credentials.
- `ACCESS_RESTRICTED`: check account permissions and eligibility; a generic 403 does not establish geography.
- `MODEL_UNAVAILABLE`: check the model setting and account access.
- `RATE_LIMITED`: inspect quota/billing and wait before retrying manually.
- `NETWORK_ERROR`: check connectivity/proxy and provider availability.
- `FAILED`: empty/unexpected response or another failure; inspect SDK configuration and dashboard status.

Free/evaluation limits depend on model and account. Consult current official [Gemini limits](https://ai.google.dev/gemini-api/docs/rate-limits), [Cohere trial limits](https://docs.cohere.com/v2/docs/rate-limits) and [Groq limits](https://console.groq.com/docs/rate-limits). Cohere's trial documentation reviewed on 2026-10-30 listed 1,000 calls/month and Command A at 20 requests/minute; the live dashboard is authoritative. Google's [region list](https://ai.google.dev/gemini-api/docs/available-regions) included Kenya when reviewed. No country restriction was established by our calls; do not bypass provider restrictions.

## Recorded verification evidence

Historical run before cleanup, **2026-10-30**, command `python scripts/verify_all_providers.py`, exit **0**. All three returned actual generated text:

| Provider | Model | Result | UTC completion |
|---|---|---|---|
| Gemini | gemini-3.5-flash-lite | SUCCESS | 2026-10-30T06:53:19.254432+00:00 |
| Cohere | command-a-03-2025 | SUCCESS | 2026-10-30T06:53:20.967973+00:00 |
| Groq | openai/gpt-oss-20b | SUCCESS | 2026-10-30T06:53:21.964952+00:00 |

Historical automated validation: 39 tests passed, including two KPI tests; syntax checks passed. One upstream Google SDK deprecation warning occurs under Python 3.14. Tested SDK versions: google-genai 1.75.0, cohere 5.21.1, groq 1.7.0.

Resolved integration issues: SDK 1.75.0's legacy Interactions schema received HTTP 400; Gemini now uses `models.generate_content` and `response.text`. Account-listed `gemini-3.8-flash` returned HTTP 503 high demand, while Flash-Lite succeeded. Groq's former `llama-3.3-70b-versatile` returned HTTP 404 (missing or inaccessible); the authenticated model list and [official reference](https://console.groq.com/docs/model/openai/gpt-oss-20b) supported the replacement. Its 1,024-token completion budget leaves room for reasoning. These errors did not establish geographic restrictions.

Security checks before cleanup found no configured keys in source/docs. `.gitignore` excludes `.env` and `.env.*` except `.env.example`. This workspace has no `.git` metadata, so tracked-file/history verification is unavailable. No commit or deployment was performed.

### After-cleanup validation (2026-10-30)

Fresh live run: `python scripts/verify_apis.py`, exit **0**, **3/3 SUCCESS** (actual nonempty generated text). These are new calls, separate from the historical run above.

| Provider | Model | Result | UTC completion |
|---|---|---|---|
| Gemini | gemini-3.5-flash-lite | SUCCESS | 2026-10-30T07:01:01.288200+00:00 |
| Cohere | command-a-03-2025 | SUCCESS | 2026-10-30T07:01:07.943929+00:00 |
| Groq | openai/gpt-oss-20b | SUCCESS | 2026-10-30T07:01:09.614257+00:00 |

`python -m pytest -q`: **39 passed**, unchanged test count. `python -m compileall -q src scripts tests pipelines`: passed. Sample pipeline: two campaigns, unchanged aggregate metrics (Galaxy A CTR 2%; Galaxy S CTR approximately 2.6667%). README command paths and CLI help checked. Configured-key scan found zero matches in source, tests, sample data and documentation. No geographic restriction was observed. No deployment or commit was performed.
