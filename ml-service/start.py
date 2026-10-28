"""Run ML experiments and tests using the existing Milestone 1 output."""

from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
PROCESSED_DATASET = PROJECT_ROOT / "data" / "processed" / "cleaned_dataset.csv"
NOTEBOOKS = (
    "notebooks/04_eda.ipynb",
    "notebooks/05_feature_engineering.ipynb",
    "notebooks/06_baseline_models.ipynb",
)


def run_step(name: str, command: list[str]) -> None:
    """Run one workflow step and stop immediately if it fails."""
    print(f"\n=== {name} ===", flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def run_parallel_steps(steps: tuple[tuple[str, list[str]], ...]) -> None:
    """Run independent workflow steps concurrently and propagate failures."""
    with ThreadPoolExecutor(max_workers=len(steps)) as executor:
        futures = {
            executor.submit(run_step, name, command): name
            for name, command in steps
        }
        for future in futures:
            future.result()


def main() -> None:
    """Run notebooks, record validation results, and test without rerunning Milestone 1."""
    if not PROCESSED_DATASET.is_file():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {PROCESSED_DATASET}. "
            "Run the Milestone 1 validation and cleaning steps first."
        )

    with tempfile.TemporaryDirectory(prefix="energy-ml-notebooks-") as output_dir:
        for notebook in NOTEBOOKS:
            run_step(
                f"Execute {notebook}",
                [
                    sys.executable,
                    "-m",
                    "jupyter",
                    "nbconvert",
                    "--to",
                    "notebook",
                    "--execute",
                    "--output-dir",
                    output_dir,
                    notebook,
                ],
            )

    run_parallel_steps((
        ("Record validation model scores", [
            sys.executable, "-m", "src.ml.train"
        ]),
        ("Run unit and API tests", [
            sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"
        ]),
    ))
    print("\nAll ML service workflow stages completed successfully.", flush=True)


if __name__ == "__main__":
    main()
