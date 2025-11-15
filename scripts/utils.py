#!/usr/bin/env python3
"""
Utility functions for organizing benchmark results.
"""

from pathlib import Path
from typing import Tuple


def get_next_run_number(results_dir: Path, prefix: str = "run_") -> int:
    """
    Get the next available run number in a directory.
    
    Args:
        results_dir: Directory containing numbered run files
        prefix: Prefix for run files (default: "run_")
    
    Returns:
        Next available run number
    """
    results_dir.mkdir(parents=True, exist_ok=True)
    
    existing_runs = list(results_dir.glob(f'{prefix}*'))
    if not existing_runs:
        return 1
    
    run_numbers = []
    for f in existing_runs:
        parts = f.stem.split('_')
        if len(parts) >= 2 and parts[1].isdigit():
            run_numbers.append(int(parts[1]))
    
    return max(run_numbers) + 1 if run_numbers else 1


def get_latest_run_file(results_dir: Path, suffix: str) -> Path:
    """
    Get the most recent run file matching a suffix.
    
    Args:
        results_dir: Directory containing run files
        suffix: File suffix to match (e.g., '_results.csv')
    
    Returns:
        Path to latest file
    
    Raises:
        FileNotFoundError: If no matching files found
    """
    files = list(results_dir.glob(f'run_*{suffix}'))
    if not files:
        raise FileNotFoundError(f"No {suffix} files found in {results_dir}")
    
    return max(files, key=lambda p: int(p.stem.split('_')[1]))


def format_run_path(results_dir: Path, run_number: int, suffix: str) -> Path:
    """
    Format a standardized run file path.
    
    Args:
        results_dir: Base directory for results
        run_number: Run number
        suffix: File suffix (e.g., '_results.csv')
    
    Returns:
        Formatted path like results_dir/run_001_results.csv
    """
    return results_dir / f'run_{run_number:03d}{suffix}'
