import sys
import time
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
VAULT_DIR = BASE_DIR / "AI-Brain-Vault"
RAW_DIR = VAULT_DIR / "Raw"
ARCHIVE_DIR = RAW_DIR / "archive"
PROCESSED_DIR = VAULT_DIR / "Processed"

ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

sys.path.append(str(BASE_DIR / "Backend"))
from LLM.LLM_Client import process_and_format

def read_raw_content(file_path: Path, retries: int = 3, delay: float = 0.5) -> str:
    for _ in range(retries):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip(): 
                    return content
        except Exception:
            pass
        time.sleep(delay)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def process_file(file_path: Path, category: str):
    print(f"-> Ingesting {file_path.name}...")

    try:
        raw_text = read_raw_content(file_path)
    except Exception as e:
        print(f"[Error] Could not read file: {e}")
        return

    print(f"-> Sending to LLM_Client to format '{category}' clipping...")
    
    try:
        # Pass file_path.name so the note can link back to it
        llm_result = process_and_format(raw_text, category, raw_filename=file_path.name)
    except Exception as e:
        print(f"[Error] LLM Processing failed: {e}")
        return

    new_file_name = llm_result["filename"]
    new_file_path = PROCESSED_DIR / new_file_name

    try:
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(llm_result["content"])
        print(f"-> Success! Saved structured note to: {new_file_name}")

        shutil.move(str(file_path), str(ARCHIVE_DIR / file_path.name))
        print("-> Archived raw file.")

    except Exception as e:
        print(f"[Error] Failed to save or archive: {e}")