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

    # Extract machine from path: test-output/{machine}/{lang_dir}/{file}
    machine = path.parent.parent.name if path.parent.parent.name != "test-output" else ""

    # Extract language from parent directory (e.g. "C_lang" -> "C")
    lang_dir = path.parent.name
    language = lang_dir.replace("_lang", "")

    thread_count = int(lines[0].split("=")[1].strip())

    runs = []
    i = 0
    while i < len(lines):
        m = re.match(r"^Run (\d+):", lines[i])
        if m:
            run_num = int(m.group(1))
            peak = float(re.search(r"Peak at bin \d+ = ([\d.]+) Hz", lines[i + 2]).group(1))
            mag = float(re.search(r"Magnitude:\s+([\d.]+)", lines[i + 4]).group(1))
            real = parse_time(re.search(r"real\s+(\S+)", lines[i + 6]).group(1))

            runs.append({
                "machine": machine,
                "language": language,
                "thread_count": thread_count,
                "run": run_num,
                "file": path.name,
                "peak_frequency": peak,
                "magnitude": mag,
                "real_time": real,
            })
            i += 1
        else:
            i += 1

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

    root = sys.argv[1] if len(sys.argv) > 1 else "test-output"
    out  = sys.argv[2] if len(sys.argv) > 2 else "benchmark_results.csv"

    runs = scan_directory(root)

    fieldnames = [
        "machine", "language", "thread_count", "run", "file",
        "peak_frequency", "magnitude", "real_time"
    ]

    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(runs)

    print(f"Wrote {len(runs)} rows to {out}")
