#!/usr/bin/env python3
import json
import os
import sys

def sort_favorites_json(filepath: str = "data/favorites.json") -> None:
    """
    Load the JSON array from `filepath`, sort its entries by the 'id' field,
    and overwrite the file with the sorted list.
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return

    # Load the JSON data
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON: {e}", file=sys.stderr)
            return

    # Ensure it's a list of dicts
    if not isinstance(data, list):
        print(f"Error: Expected a JSON array in {filepath}", file=sys.stderr)
        return

    # Sort by the 'id' key (missing or non-int ids sort to 0)
    sorted_data = sorted(
        data,
        key=lambda entry: entry.get("id", 0)
    )

    # Write the sorted list back to the file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully sorted {len(sorted_data)} entries by 'id' in {filepath}.")

if __name__ == "__main__":
    # You can pass an alternate path as the first argument
    json_path = sys.argv[1] if len(sys.argv) > 1 else "data/favorites.json"
    sort_favorites_json(json_path)
