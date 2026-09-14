from datetime import datetime
import json
from pathlib import Path

def Log_Event_Detection(LOGS_DIR, LOG_FILE_PATH, category: str, file_name: str, file_path: Path):
    """Appends a new event record to the JSONL log file without rewriting historical logs."""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": category,
        "file_name": file_name,
        "file_path": str(file_path),
    }

    # Ensure the Logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
