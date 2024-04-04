from pathlib import Path

# Folders
ROOT = Path(__file__, "..", "..", "..", "..").resolve()
FOLDER_SECRETS = Path(ROOT, "config", "secrets")
FOLDER_DOCS_RAG_SOURCES = Path(ROOT, "docs", "rag_sources")

# Files
FILE_METADATA_AI_CORE_KEY = Path(
    FOLDER_SECRETS, "my_metadata_ai_core_key.json"
).resolve()
FILE_ENV = Path(FOLDER_SECRETS, ".env").resolve()
