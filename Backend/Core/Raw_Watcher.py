import time
import sys
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path  

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from Backend.Util.Util import Log_Event_Detection 
from Backend.Core.Raw_Process import process_file

# Dynamic paths derived from the repository root
VAULT_DIR = BASE_DIR / "AI-Brain-Vault"
CLIPPINGS_DIR_PATH = VAULT_DIR / "Raw" / "clippings"
LOGS_DIR = BASE_DIR / "Logs"
LOG_FILE_PATH = LOGS_DIR / "Jarvis_Logs.jsonl"


class RawFolderHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if file_path.suffix in [".md", ".txt"]:
            category = file_path.parent.name.lower()

            print(f"\n[Jarvis Event] New '{category}' clipping detected: {file_path.name}")
            Log_Event_Detection(LOGS_DIR, LOG_FILE_PATH, category, file_path.name, file_path)

            process_file(file_path, category)


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