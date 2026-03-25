# Author: Jerry Onyango
# Contribution: Runs production batch training, artifact save/load, and inference validation for the energy ML path.
from pathlib import Path

from ml_pipeline import ProductionBatchEnergyModel, load_training_rows


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_path = root / "data" / "sample_training_readings.csv"
    artifact_path = root / "artifacts" / "models" / "smoke_model.json"
    rows = load_training_rows(data_path)

    pipeline = ProductionBatchEnergyModel()
    pipeline.fit_in_batches(rows, batch_size=4)
    pipeline.save(artifact_path)

    loaded_model = ProductionBatchEnergyModel.load(artifact_path)
    metrics = loaded_model.evaluate(rows)
    predictions = loaded_model.predict(rows[:5])
    suggestions = loaded_model.suggest(rows)

    if artifact_path.exists():
        artifact_path.unlink()

    print({
        "training_rows": len(rows),
        "mae_kw": metrics["mae_kw"],
        "mape": metrics["mape"],
        "sample_predictions": [round(value, 2) for value in predictions],
        "suggestions": len(suggestions),
    })


if __name__ == "__main__":
    main()
