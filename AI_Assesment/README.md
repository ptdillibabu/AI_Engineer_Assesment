# Deliberation Engine

A multi-agent AI system that transforms vague feature requests into structured decision documents through simulated dialogue between a Proposer and Critic.

## Quick Start

### Prerequisites

- Python 3.10 or later
- pip (package installer)
- A virtual environment (recommended)

Required environment variables (store in a `.env` file):
- `OPENAI_API_KEY` — OpenAI API key (optional if not using OpenAI)
- `ANTHROPIC_API_KEY` — Anthropic / Claude API key (optional)
- `GOOGLE_API_KEY` — Google Generative (Gemini) API key (optional)
- `AZURE_OPENAI_ENDPOINT` — Azure OpenAI endpoint (optional)
- `AZURE_OPENAI_API_VERSION` — Azure OpenAI API version (optional)
- `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_SCOPE` — `Azure AD credentials/scope` (optional)

Install runtime dependencies:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
# source venv/bin/activate

pip install -r requirements.txt
python -m src.main or python -m src.main --request "The CRM should alert us when our relationship with a country goes cold."

## Prompts

- **System prompts:** Stored as Markdown files under the `prompts/` directory (these are used as the agent *system* role templates).
- **User-message templates:** Centralized in the `src/prompts_templates/` package. These provide the formatted user messages sent each round (e.g. initial proposer prompt, critic review template, summarizer synthesis template).

## Configuration

- **Location:** [config/settings.yaml] — edit this file to change application defaults.
- **What to update:** **Feature request** (default input),
 **LLM provider/model/temperature/max_tokens**, 
 **Deliberation** (`min_rounds`, `max_rounds`, `use_summarizer`), 
 and **Output** (`format`, `save_trace`, `trace_dir`).

 ##DESICIONS.md
  - ** requested information Stored as Markdown files under the `prompts/`
 ##Output
   - ** sample run output of traces for each input case available under the `output/`
