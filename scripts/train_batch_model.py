# Author: Jerry Onyango
# Contribution: Trains the production batch model from CSV in chunks and saves a reusable model artifact.
from __future__ import annotations

import argparse

from ml_pipeline import train_model_from_csv_batches


def main() -> None:
    parser = argparse.ArgumentParser(description="Train production batch energy model")
    parser.add_argument("--input", required=True, help="Path to training CSV")
    parser.add_argument("--output", required=True, help="Path to output model artifact JSON")
    parser.add_argument("--batch-size", type=int, default=5000, help="Batch size for incremental training")
    args = parser.parse_args()

    model = train_model_from_csv_batches(args.input, batch_size=args.batch_size)
    artifact_path = model.save(args.output)
    print({
        "artifact": str(artifact_path),
        "training_rows": model.training_rows,
        "training_mape": model.training_mape,
        "note": "Use scripts/predict_batch_model.py for prediction checks.",
    })


if __name__ == "__main__":
    main()
