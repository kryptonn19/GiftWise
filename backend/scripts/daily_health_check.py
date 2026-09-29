#!/usr/bin/env python3
"""
Daily Health Check Script for GiftWise repository.
Runs tests, collects codebase metrics, and appends an entry to HEALTH_STATUS.md.
"""
import sys
import os
import subprocess
from datetime import datetime, timezone

# Ensure project root is in PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

HEALTH_FILE = os.path.join(PROJECT_ROOT, "HEALTH_STATUS.md")


def run_tests():
    """Runs pytest and returns test output and status code."""
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "backend/tests", "-q", "--no-header"],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout + result.stderr


def count_files(directory, extension):
    """Count files with given extension in a directory recursively."""
    count = 0
    if not os.path.exists(directory):
        return count
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(extension):
                count += 1
    return count


def update_health_file(test_passed: bool, test_output: str):
    """Updates HEALTH_STATUS.md with current status and log entry."""
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    py_file_count = count_files(os.path.join(PROJECT_ROOT, "backend"), ".py")
    test_file_count = count_files(os.path.join(PROJECT_ROOT, "backend", "tests"), ".py")

    status_str = "PASSED ✅" if test_passed else "FAILED ❌"

    # Summarize last line of pytest output if available
    lines = [l.strip() for l in test_output.strip().split("\n") if l.strip()]
    summary_line = lines[-1] if lines else "No output"

    entry_markdown = f"| `{date_str}` | {now_utc} | {status_str} | `{summary_line}` |\n"

    header_content = f"""# 🟢 GiftWise Daily Health Status

> **Automated Health Check & Maintenance Log**
> This file is updated daily by GitHub Actions to verify test suite passing status and codebase integrity.

### 📊 Current Overview
- **Last Run Timestamp**: `{now_utc}`
- **Test Suite Status**: {status_str}
- **Python Source Files**: `{py_file_count}`
- **Test Files**: `{test_file_count}`

---

### 📜 Daily Execution History
| Date | Timestamp (UTC) | Test Status | Summary |
| :--- | :--- | :--- | :--- |
"""

    existing_rows = []
    if os.path.exists(HEALTH_FILE):
        try:
            with open(HEALTH_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if "| Date | Timestamp" in content:
                    parts = content.split("| Date | Timestamp (UTC) | Test Status | Summary |")
                    if len(parts) > 1:
                        table_part = parts[1].split("\n| :---")[1] if "\n| :---" in parts[1] else parts[1]
                        rows = [r for r in table_part.strip().split("\n") if r.startswith("|")]
                        # Keep maximum 30 historical log entries
                        existing_rows = [r + "\n" for r in rows if r and not r.startswith(f"| `{date_str}`")]
        except Exception as e:
            print(f"Warning reading existing HEALTH_STATUS.md: {e}")

    # Write new file content
    with open(HEALTH_FILE, "w", encoding="utf-8") as f:
        f.write(header_content)
        f.write(entry_markdown)
        for row in existing_rows[:29]:
            f.write(row)

    print(f"Successfully updated {HEALTH_FILE} at {now_utc}")


def main():
    print("Starting daily health check...")
    passed, output = run_tests()
    print(f"Tests execution completed. Passed: {passed}")
    update_health_file(passed, output)


if __name__ == "__main__":
    main()
