# AG News Intelligence Pipeline

A robust, enterprise-grade machine learning classification and extraction pipeline built for the **AG News Dataset**. This project leverages modern Large Language Models (LLMs) via the Groq API to seamlessly categorize news articles, extract structured entities, and determine sentiment with strict JSON safeguards and intelligent regex fallbacks.

## ✨ Key Features
- **Unified CLI (`run.py`)**: A single entry point for evaluation, interactive analysis, and serving the API.
- **Integrated Frontend**: The dashboard is natively served from the FastAPI backend at the root route (`/`).
- **Resilient AI Pipeline**: Features `tenacity` exponential backoffs, API rate limit bypass mechanisms, and Regex-salvaging for broken JSON generations.
- **Deep Extraction**: Automatically extracts topic keywords, Named Entities (NER), Summary, Sentiment, and Breaking News status from text.
- **Dual Support**: Configured to dynamically support models from both Groq and Gemini.

---

## 🚀 Prerequisites

- Python 3.10+
- Add your API Keys to a `.env` file in the root directory:
```env
GROQ_API_KEY="your_groq_key_here"
GEMINI_API_KEY="your_gemini_key_here"
```
*(The system currently defaults to using the Groq API model for maximum speed).*

---

## 🛠️ Unified CLI Usage

The entire application has been standardized to operate cleanly through `run.py`.

### 1. Launch the Server Dashboard (API + Frontend)
```bash
python run.py serve
```
- **Web Dashboard**: Open `http://localhost:8000/` in your browser.
- **API Swagger Docs**: `http://localhost:8000/docs`
- **Predict Route**: `POST http://localhost:8000/api/v1/predict`
- **Extract Route**: `POST http://localhost:8000/api/v1/extract`

### 2. Evaluate Pipeline Accuracy (Batch Processing)
Run a batch test on the official AG News test split to determine model accuracy. 
*Note: Due to API rate limits (e.g. 30 requests/minute on free tier), it is highly recommended to use the `--delay` flag.*
```bash
python run.py evaluate --limit 100 --batch-size 10 --delay 2.5
```

### 3. Analyze a Single Article
Test the end-to-end pipeline (classification + extraction) instantly from the terminal.
```bash
python run.py analyze "Apple unveils brand new M4 AI processing chip at developer conference."
```

---

## 🐳 Docker Deployment

The system is fully containerized and production ready.

**Using Docker Compose (Recommended):**
```bash
docker compose up --build
```
The API and Frontend will automatically become available at `http://localhost:8123`.

**Using pure Docker:**
```bash
docker build -t ag-news-api .
docker run --rm -d --name ag-news-api -p 8123:8000 --env-file .env ag-news-api
```

---

## 🔥 System Architecture
1. **app/api**: FastAPI routes detailing `/predict` and `/extract`.
2. **app/pipeline**: The core LLM integration, heavily customized with tailored Few-Shot examples, JSON structural grounding, and Regex formatting salvaging for LLM failures.
3. **app/frontend**: Vanilla HTML/JS frontend application that is injected seamlessly via FastAPI StaticFiles.
4. **app/schemas**: Strict Pydantic models for request/response validation mapping to News Categories.
