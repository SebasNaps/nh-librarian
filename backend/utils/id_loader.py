
from backend.utils.logger import logger

import json

def extract_ids_from_file(filepath) -> list:
    ids = []

    try:
        # Try reading as JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list) and all(isinstance(item, dict) and "id" in item for item in data):
            ids = [item["id"] for item in data]
            return ids
        else:
            print("JSON structure is not a list of dicts with 'id'")
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass  # Not a JSON file or invalid JSON

    # If not JSON, try reading as plain text
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ids = [line.strip() for line in f if line.strip()]
        return ids
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise ValueError(f"Failed to read file: {e}")

# # Example usage:
# file_path = "your_file.json"  # or "your_file.txt"
# ids = extract_ids_from_file(file_path)
# print("Extracted IDs:", ids)
