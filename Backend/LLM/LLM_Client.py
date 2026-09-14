import json
from pathlib import Path
from ollama import chat
from pydantic import BaseModel, Field

# 1. Define a robust schema for structured extraction
class NoteSchema(BaseModel):
    filename: str = Field(description="A short, descriptive file name ending in .md, using underscores instead of spaces")
    title: str = Field(description="A clean, engaging title for the note")
    summary: str = Field(description="A 1-2 paragraph comprehensive summary of the core concepts")
    key_takeaways: list[str] = Field(description="List of 3 to 5 key actionable insights or technical concepts")
    related_links: list[str] = Field(description="List of broad topics or entities to turn into Obsidian wikilinks")

def load_schema_instructions(category: str) -> str:
    """Loads additional prompt guidelines from the Schemas folder if they exist."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    template_path = base_dir / "Schemas" / f"{category}.md"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Extract a detailed summary, key takeaways, and related concepts from this text."

def process_and_format(raw_text: str, category: str, raw_filename: str, model_name: str = "hermes3") -> dict:
    """Queries Ollama with strict schema enforcement and returns structured data."""
    custom_instructions = load_schema_instructions(category)
    
    system_prompt = (
        f"You are an expert technical knowledge curator.\n"
        f"{custom_instructions}\n\n"
        "Ensure your output strictly conforms to the requested JSON schema."
    )
    
    response = chat(
        model=model_name,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"Raw Content to parse:\n\n{raw_text}"}
        ],
        format=NoteSchema.model_json_schema(),
        options={'temperature': 0}
    )
    
    # Validate via Pydantic
    parsed_data = NoteSchema.model_validate_json(response['message']['content'])
    
    # Ensure filename safety and extension
    safe_filename = parsed_data.filename.strip().replace(" ", "_")
    if not safe_filename.endswith(".md"):
        safe_filename += ".md"
        
    # Build the final Obsidian-native markdown string locally in Python
    # This guarantees your vault format, collapsible callouts, and explicit back-links exist!
    markdown_content = f"""---
tags: [{category}, learning]
status: review
source: "youtube"
---

# {parsed_data.title}

## 📝 Summary
{parsed_data.summary}

## 💡 Key Takeaways
"""
    for takeaway in parsed_data.key_takeaways:
        markdown_content += f"- {takeaway}\n"

    markdown_content += f"""
## 🔗 Related Links & Vault Graph
"""
    for link in parsed_data.related_links:
        markdown_content += f"- [[{link}]]\n"

    # Add the explicit workflow link pointing back to the raw source file in the archive
    markdown_content += f"""
---
### 🗄️ Source Reference
- **Archived Raw File**: [[{raw_filename}]]
"""

    return {
        "filename": safe_filename,
        "content": markdown_content.strip()
    }