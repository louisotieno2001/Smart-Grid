# Author: Jerry Onyango
# Contribution: Loads a trained production model artifact and evaluates prediction/suggestion quality on a CSV dataset.
from __future__ import annotations

import argparse

from ml_pipeline import ProductionBatchEnergyModel, load_training_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict/evaluate using production batch model")
    parser.add_argument("--model", required=True, help="Path to model artifact JSON")
    parser.add_argument("--input", required=True, help="Path to evaluation CSV")
    args = parser.parse_args()

    model = ProductionBatchEnergyModel.load(args.model)
    rows = load_training_rows(args.input)
    metrics = model.evaluate(rows)
    predictions = model.predict(rows[:5])
    suggestions = model.suggest(rows)

    print(
        {
            "rows": len(rows),
            "mae_kw": metrics["mae_kw"],
            "mape": metrics["mape"],
            "sample_predictions": [round(pred, 2) for pred in predictions],
            "suggestions": len(suggestions),
        }
    )


if __name__ == "__main__":
    main()
