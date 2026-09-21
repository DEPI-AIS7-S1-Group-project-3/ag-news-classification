# AG News Intelligence Pipeline

A pipeline that classifies news articles from the AG News dataset and pulls structured information out of them using LLMs (Groq by default, Gemini optional). For each article it returns a category, keywords, named entities, a short summary, the sentiment, and whether it reads as breaking news.

LLMs sometimes return malformed JSON or hit rate limits, so the pipeline is built to survive both: failed calls are retried with exponential backoff, and when the JSON comes back broken, a regex fallback recovers the fields it can instead of failing the request.

## Features

- **One CLI for everything.** `run.py` handles serving the app, evaluating accuracy, and analyzing a single article.
- **API and dashboard in one server.** FastAPI serves the REST API and the web dashboard together, so there is nothing separate to deploy.
- **Classification.** Assigns each article to one of the four AG News categories: World, Sports, Business, Sci/Tech.
- **Extraction.** Returns keywords, named entities, a summary, sentiment, and a breaking-news flag.
- **Failure handling.** Retries with exponential backoff (`tenacity`), configurable delays between requests for rate-limited tiers, and regex recovery for broken JSON output.
- **Two providers.** Works with Groq and Gemini models. Groq is the default because it is faster.

## Getting started

### Requirements

- Python 3.10 or newer
- A Groq API key (and optionally a Gemini API key)

### Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY="your_groq_key_here"
GEMINI_API_KEY="your_gemini_key_here"
```

Only the key for the provider you use is required. The pipeline uses Groq unless you configure it otherwise.

## Usage

All commands go through `run.py`.

### Run the server

```bash
python run.py serve
```

| What | Where |
|---|---|
| Web dashboard | http://localhost:8000/ |
| Swagger docs | http://localhost:8000/docs |
| Classify an article | `POST /api/v1/predict` |
| Extract entities, sentiment, etc. | `POST /api/v1/extract` |

### Evaluate accuracy

Runs the pipeline against the official AG News test split and reports accuracy.

```bash
python run.py evaluate --limit 100 --batch-size 10 --delay 2.5
```

| Flag | What it does |
|---|---|
| `--limit` | How many test articles to evaluate |
| `--batch-size` | How many articles to process per batch |
| `--delay` | Seconds to wait between requests |

On free API tiers you can be limited to around 30 requests per minute, so set `--delay` or the run will keep hitting rate limits.

### Analyze a single article

Runs classification and extraction on one piece of text and prints the result in the terminal.

```bash
python run.py analyze "Apple unveils brand new M4 AI processing chip at developer conference."
```

## Docker

With Docker Compose (recommended):

```bash
docker compose up --build
```

Without Compose:

```bash
docker build -t ag-news-api .
docker run --rm -d --name ag-news-api -p 8123:8000 --env-file .env ag-news-api
```

Either way, the dashboard and API are at http://localhost:8123. The container listens on port 8000 internally and is mapped to 8123 on your machine.

## Project structure

```
app/
  api/        FastAPI routes for /predict and /extract
  pipeline/   LLM calls, few-shot prompts, JSON validation, regex fallback
  frontend/   Vanilla HTML/JS dashboard, served by FastAPI as static files
  schemas/    Pydantic models for requests, responses, and news categories
run.py        CLI entry point (serve, evaluate, analyze)
```

## How the pipeline works

1. The article text is sent to the LLM with few-shot examples and a strict JSON output format.
2. If the call fails or is rate limited, it is retried with exponential backoff.
3. The response is parsed and validated against the Pydantic schemas.
4. If the JSON is malformed, regex extraction recovers the fields that are still readable.
5. The validated result is returned by the API, the CLI, or the dashboard.
