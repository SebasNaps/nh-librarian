
from backend.utils.logger import logger

import json
import os
from typing import Union

def append_data(filename, new_entries: Union[dict, list]):

    if not new_entries:
        return
    dir = os.path.dirname(filename)
    logger.info(f"Saving data to {filename}")
    # Load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []  # File is empty or invalid
    else:
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
        data = []


    # Ensure data is a list
    if not isinstance(data, list):
        logger.error(f"JSON file {filename} does not contain a list of entries")
        raise ValueError("JSON file does not contain a list of entries")

    # Check if entry with the same id already exists
    existing_ids = {entry.get("id") for entry in data if isinstance(entry, dict)}

    if isinstance(new_entries, dict):
        new_entries = [new_entries]
    
    for new_entry in new_entries:
        if new_entry:
            if new_entry.get("id") in existing_ids:
                logger.warning(f"Entry with id {new_entry['id']} already exists. Skipping append.")
            else:
                data.append(new_entry)
                logger.info(f"Appended entry with id {new_entry['id']}")

    # Append new entry and save
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def read_data(filename: str) -> list:
    # Load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []  # File is empty or invalid
    else:
        data = []


    # Ensure data is a list
    if not isinstance(data, list):
        logger.error(f"JSON file {filename} does not contain a list of entries")
        raise ValueError("JSON file does not contain a list of entries")

    logger.info(f"Loaded data in {filename}.")
    return data

# # Example usage
# new_entry = {
#     "id": 567876,
#     "title": "Kimi to Himitsu no Upload 2 / Our Secret Upload 2",
#     "title_en": "[nikukyu (Shinima)] Kimi to Himitsu no Upload 2 / Our Secret Upload 2 [Digital] [English] {Doujins.com}",
#     "title_jp": "[nikukyu (\u3057\u306b\u307e)] \u541b\u3068\u79d8\u5bc6\u306e\u30a2\u30c3\u30d7\u30ed\u30fc\u30c9\u2461 [DL\u7248] [\u82f1\u8a33]",
#     "author": ["shinima"],
#     "languages": ["english", "translated"],
#     "tags": [
#         "nakadashi", "femdom", "defloration", "multi-work series",
#         "blowjob", "yandere", "sole male"
#     ]
# }

# append_metadata("metadata.json", new_entry)
