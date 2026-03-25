# Author: Jerry Onyango
# Contribution: Exposes ROI calculator public interfaces for reuse by CLI and other modules.
from .calculator import calculate_roi, build_proposal
from .models import ROIInput, ROIOutput, SensitivityCase

__all__ = [
    "calculate_roi",
    "build_proposal",
    "ROIInput",
    "ROIOutput",
    "SensitivityCase",
]
