"""
Evaluate the classification pipeline against real AG News test samples.

Usage:
    python evaluate.py --limit 100
    python evaluate.py --limit 200 --split test --out results.csv

Run this from the project root (same folder as app/), with the venv active
and GROQ_API_KEY set in .env.
"""

import argparse
import csv
import time

from app.ingestion.load_data import fetch_ag_news_data
from app.services.run_pipeline import run_pipeline_batch


def evaluate(limit: int, split: str, out_path: str | None, delay: float, batch_size: int):
    print(f"Loading {limit} samples from AG News ({split} split)...")
    df = fetch_ag_news_data(split=split, limit=limit)

    total = len(df)
    correct = 0
    fallback_count = 0
    confusion = {}  # (true_label, predicted_label) -> count
    rows = []

    start = time.perf_counter()
    texts = df["text"].tolist()
    results = run_pipeline_batch(texts, batch_size=batch_size, delay_seconds=delay)

    for i, (row, result) in enumerate(zip(df.to_dict("records"), results), start=1):
        text = row["text"]
        true_label = row["label_name"]
        predicted = result["category"]

        is_correct = predicted == true_label
        correct += int(is_correct)
        fallback_count += int(result["used_fallback"])

        key = (true_label, predicted)
        confusion[key] = confusion.get(key, 0) + 1

        rows.append({
            "text": text[:80],
            "true_label": true_label,
            "predicted": predicted,
            "confidence": result["confidence"],
            "used_fallback": result["used_fallback"],
            "correct": is_correct,
        })

        status = "OK" if is_correct else "WRONG"
        fb = " [FALLBACK]" if result["used_fallback"] else ""
        print(f"[{i}/{total}] {status}{fb} | true={true_label} pred={predicted} "
              f"conf={result['confidence']}")

    elapsed = time.perf_counter() - start

    print("\n" + "=" * 50)
    print(f"Accuracy:      {correct}/{total} = {correct / total:.2%}")
    print(f"Fallback rate: {fallback_count}/{total} = {fallback_count / total:.2%}")
    print(f"Total time:    {elapsed:.1f}s ({elapsed / total:.2f}s per sample)")
    print("=" * 50)

    print("\nConfusion (true -> predicted):")
    for (true_label, predicted), count in sorted(confusion.items()):
        marker = "" if true_label == predicted else "  <-- mismatch"
        print(f"  {true_label:10s} -> {predicted:10s} : {count}{marker}")

    if out_path:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nDetailed results saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100, help="Number of samples to evaluate")
    parser.add_argument("--split", type=str, default="test", help="Dataset split (train/test)")
    parser.add_argument("--out", type=str, default="eval_results.csv", help="CSV output path")
    parser.add_argument("--delay", type=float, default=2.0,
                         help="Seconds to wait between each batch to reduce Groq rate-limit pressure.")
    parser.add_argument("--batch-size", type=int, default=2,
                         help="Number of texts to process per batch before pausing.")
    args = parser.parse_args()

    evaluate(limit=args.limit, split=args.split, out_path=args.out, delay=args.delay, batch_size=args.batch_size)