# AG News Classification API

## Prerequisites

- Python 3.13+
- Docker Desktop (optional for container mode)
- A Groq API key in a `.env` file in this directory:

```bash
GROQ_API_KEY=your_key_here
```

## Run locally

```bash
cd ag-news-classification
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Then open:
- API root: http://localhost:8001/
- Status: http://localhost:8001/api/v1/status
- Predict: http://localhost:8001/api/v1/predict

## Run with Docker

```bash
cd ag-news-classification
docker build -t ag-news-api .
docker run --rm -d --name ag-news-api -p 8123:8001 --env-file .env ag-news-api
```

Then use:
- API: http://localhost:8123/
- Status: http://localhost:8123/api/v1/status

Serve the frontend separately on a free port:

```bash
cd ag-news-classification/app/frontend
python3 -m http.server 9090
```

Open http://localhost:9090 and use the default API URL on the page:

```text
http://localhost:8123/api/v1/predict
```

## Run with Docker Compose

```bash
cd ag-news-classification
docker compose up --build
```

## Troubleshooting

- `Bind for 0.0.0.0:8001 failed: port is already allocated`
  - Stop the process using the port or switch to another free host port.
- `GROQ_API_KEY is not set`
  - Make sure `.env` exists and contains `GROQ_API_KEY=...` with no spaces around `=`.

## Quick smoke test

```bash
curl http://localhost:8001/api/v1/status
curl -X POST http://localhost:8001/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"Apple unveils new AI chip for data centers."}'
```
