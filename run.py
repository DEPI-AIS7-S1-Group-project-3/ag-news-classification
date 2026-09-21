import argparse
import sys
import json

def main():
    parser = argparse.ArgumentParser(description="AG News Classification & Extraction Pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: serve
    serve_parser = subparsers.add_parser("serve", help="Start the FastAPI API server")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    # Subcommand: evaluate
    eval_parser = subparsers.add_parser("evaluate", help="Run batch evaluation over a dataset")
    eval_parser.add_argument("--limit", type=int, default=40, help="Number of records to process")
    eval_parser.add_argument("--split", default="test", help="Dataset split (train or test)")
    eval_parser.add_argument("--out", default=None, help="Output CSV path for results")
    eval_parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests to avoid rate limits")
    eval_parser.add_argument("--batch-size", type=int, default=5, help="Batch size for Groq requests")

    # Subcommand: analyze
    analyze_parser = subparsers.add_parser("analyze", help="Run the full pipeline (classification + extraction) on a single string of text")
    analyze_parser.add_argument("text", help="The text string to analyze")
    
    args = parser.parse_args()

    if args.command == "serve":
        import uvicorn
        print(f"Starting server on {args.host}:{args.port}...")
        uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)
        
    elif args.command == "evaluate":
        from evaluate import evaluate
        evaluate(limit=args.limit, split=args.split, out_path=args.out, delay=args.delay, batch_size=args.batch_size)
        
    elif args.command == "analyze":
        # Check environment variables
        import os
        if not os.environ.get("GROQ_API_KEY"):
            from dotenv import load_dotenv
            load_dotenv()
            
        from app.services.run_pipeline import run_pipeline
        from app.pipeline.retry import extract_with_retry
        
        print("\n=== CLASSIFICATION ===")
        classification_result = run_pipeline(args.text)
        if hasattr(classification_result, "model_dump"):
            print(json.dumps(classification_result.model_dump(), indent=2))
        else:
            print(json.dumps(classification_result, indent=2))
        
        print("\n=== EXTRACTION ===")
        try:
            extraction_result = extract_with_retry(args.text)
            print(json.dumps(extraction_result.model_dump(), indent=2))
        except Exception as e:
            print(f"Extraction failed: {e}")
            
if __name__ == "__main__":
    main()
