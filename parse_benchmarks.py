import re
import glob
from pathlib import Path


def parse_time(time_str):
    """Convert '0m0.101s' to float seconds."""
    m, s = time_str.rstrip("s").split("m")
    return int(m) * 60 + float(s)


def parse_benchmark_file(path):
    """Parse a single benchmark result file. Returns a list of run dicts."""
    path = Path(path)
    text = path.read_text()
    lines = text.splitlines()

    language = path.stem.split("_benchmark_results")[0]
    n = int(lines[0].split("=")[1].strip())

    runs = []
    for integral_match, time_match in zip(
        re.finditer(r"^of the integral .+=\s*([\d.]+)\s*$", text, re.MULTILINE),
        re.finditer(r"^real\s+(\S+)", text, re.MULTILINE),
    ):
        runs.append({
            "language": language,
            "n": n,
            "file": path.name,
            "integral": float(integral_match.group(1)),
            "real_time": parse_time(time_match.group(1)),
        })

    return runs


def scan_directory(root):
    """Scan all benchmark result .txt files under root. Returns flat list of run dicts."""
    results = []
    for filepath in sorted(glob.glob(f"{root}/**/*.txt", recursive=True)):
        results.extend(parse_benchmark_file(filepath))
    return results


if __name__ == "__main__":
    import sys
    import csv

    root = sys.argv[1] if len(sys.argv) > 1 else "test-output/mac-mini"
    out  = sys.argv[2] if len(sys.argv) > 2 else "benchmark_results.csv"

    runs = scan_directory(root)

    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["language", "n", "file", "integral", "real_time"])
        writer.writeheader()
        writer.writerows(runs)

    print(f"Wrote {len(runs)} rows to {out}")
