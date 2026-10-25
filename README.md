# Multimodal Construction Intelligence Platform

Skill Wallet Capstone Project 1 — Streamlit prototype.

## Features
- PPE / site safety audit with structured JSON output and downloadable report
- Concrete crack triage with cautious defect classification and engineering-review actions
- Indicative construction budget, CapEx, market-value estimate, steel and cement thumb rules
- Weather-aware advisory and multi-turn site assistant
- Gemini API key input in sidebar; demo mode works without a key
- No external database required

## Run locally
Python 3.9+ is recommended (Python 3.10+ also works).

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Gemini API
Obtain a key from Google AI Studio and paste it into the password field in the sidebar. The app calls the Gemini REST API from the current Streamlit session. Do not commit API keys to source control.

The configured model is `gemini-1.5-flash`; model availability can change. If Google retires or restricts that model for your key/project, update `GEMINI_MODEL` near the top of `app.py` to a currently supported multimodal Gemini model.

## Deploy on Streamlit Community Cloud
1. Push `app.py`, `requirements.txt`, and `.streamlit/config.toml` to a GitHub repository.
2. In Streamlit Community Cloud, create an app and select the repository, branch and `app.py`.
3. Deploy. Paste your Gemini key in the app sidebar when needed.

## Important limitations
- Demonstration mode data is illustrative and is not inferred from the uploaded image.
- Construction and valuation assumptions are broad thumb rules, not a bill of quantities, contractor quotation, formal valuation or engineering design.
- Photo-only AI cannot certify PPE compliance, structural integrity, or legal compliance. Follow applicable local law, site procedures, and qualified professional advice.
- The Pollinations/Flux integration is represented as a prompt generator only; the app does not currently make an image-generation API call.
- The weather selector is manual and is not a live forecast integration.
