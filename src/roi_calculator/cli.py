# Author: Jerry Onyango
# Contribution: Provides command-line entrypoint for loading ROI inputs and emitting proposal outputs.
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .calculator import build_proposal
from .models import ROIInput


def _read_inputs(path: str) -> ROIInput:
    payload = json.loads(Path(path).read_text())
    return ROIInput(**payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Energy ROI calculator")
    parser.add_argument("--input", required=True, help="Path to ROI input JSON")
    parser.add_argument("--output", required=False, help="Optional output JSON path")
    args = parser.parse_args()

    roi_input = _read_inputs(args.input)
    proposal = build_proposal(roi_input)
    formatted = json.dumps(proposal, indent=2)

    if args.output:
        Path(args.output).write_text(formatted + "\n")
    else:
        print(formatted)


if __name__ == "__main__":
    main()
