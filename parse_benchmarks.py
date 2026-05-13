import re
import glob
from pathlib import Path
import statistics as stat
from collections import defaultdict
import sys
import csv

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
            block = "\n".join(lines[i + 1:i + 11])
            peak_m = re.search(r"Peak at bin \d+ = ([\d.]+) Hz", block)
            mag_m  = re.search(r"Magnitude:\s+([\d.]+)", block)
            real_m = re.search(r"real\s+(\S+)", block)
            if peak_m and mag_m and real_m:
                runs.append({
                    "machine": machine,
                    "language": language,
                    "thread_count": thread_count,
                    "run": run_num,
                    "file": path.name,
                    "peak_frequency": float(peak_m.group(1)),
                    "magnitude": float(mag_m.group(1)),
                    "real_time": parse_time(real_m.group(1)),
                })
        i += 1

    return runs


def scan_directory(root):
    """Scan all benchmark result .txt files under root. Returns flat list of run dicts."""
    results = []
    for filepath in sorted(glob.glob(f"{root}/**/*.txt", recursive=True)):
        results.extend(parse_benchmark_file(filepath))
    return results


def compute_stats(runs):
    """Group runs by (language, thread_count) and compute mean + stdev of real_time."""
    
    groups = defaultdict(list)
    for r in runs:
        key = (r["language"], r["thread_count"], r["machine"])
        groups[key].append(r["real_time"])

    stats = []
    for (lang, tc, mach), times in sorted(groups.items()):
        row = {
            "machine": mach,
            "language": lang,
            "thread_count": tc,
            "run_count": len(times),
            "mean_real_time": round(stat.mean(times), 6),
        }
        try:
            row["stdev_real_time"] = round(stat.stdev(times), 6)
        except stat.StatisticsError:
            row["stdev_real_time"] = ""
        stats.append(row)

    return stats


if __name__ == "__main__":
    
    root = sys.argv[1] if len(sys.argv) > 1 else "test-output"
    out  = sys.argv[2] if len(sys.argv) > 2 else "benchmark_results.csv"
    stats_out = sys.argv[3] if len(sys.argv) > 3 else "benchmark_stats.csv"

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

    stats = compute_stats(runs)

    stats_fields = ["machine", "language", "thread_count", "run_count", "mean_real_time", "stdev_real_time"]
    with open(stats_out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=stats_fields)
        writer.writeheader()
        writer.writerows(stats)

    print(f"Wrote {len(stats)} rows to {stats_out}")
