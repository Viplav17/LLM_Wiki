import time
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

# Base directory: Backend/Core/Raw_Watcher.py -> Core (parent) -> Backend (parent) -> LLM_Wiki (parent)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Dynamic paths derived from the repository root
VAULT_DIR = BASE_DIR / "AI-Brain-Vault"
CLIPPINGS_DIR_PATH = VAULT_DIR / "Raw" / "clippings"
LOGS_DIR = BASE_DIR / "Logs"
LOG_FILE_PATH = LOGS_DIR / "Jarvis_Logs.jsonl"


def log_event(category: str, file_name: str, file_path: Path):
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


class RawFolderHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if file_path.suffix in [".md", ".txt"]:
            category = file_path.parent.name

            print(f"\n[Jarvis Event] New '{category}' clipping detected: {file_path.name}")
            log_event(category, file_path.name, file_path)


def start_watching():
    # Ensure the clippings directory exists
    if not CLIPPINGS_DIR_PATH.exists():
        print(f"Creating directory: {CLIPPINGS_DIR_PATH}")
        CLIPPINGS_DIR_PATH.mkdir(parents=True, exist_ok=True)

    event_handler = RawFolderHandler()
    observer = Observer()

    observer.schedule(event_handler, path=str(CLIPPINGS_DIR_PATH), recursive=True)

    print(f"Monitoring '{CLIPPINGS_DIR_PATH}' and subfolders for new clippings...")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Stopping watcher...")
    observer.join()


if __name__ == "__main__":
    start_watching()
