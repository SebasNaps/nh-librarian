import requests
import datetime
from backend.utils.logger import logger

# Base endpoints
API_BASE_URL = "https://nhentai.net/api/gallery"
GALLERY_BASE_URL = "https://nhentai.net/g"


def get_metadata(doujin_id: int) -> dict | None:
    """
    Fetch and parse metadata for a given doujin ID from NHentai API.

    Returns a dict with structured metadata, or None on failure.
    """
    logger.info(f"Doujin {doujin_id}: fetching metadata...")

    url = f"{API_BASE_URL}/{doujin_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as err:
        logger.error(f"Failed to fetch metadata for ID {doujin_id}: {err}")
        return None

    data = response.json()
    tags = data.get("tags", [])

    # Helper to filter tag names by tag type
    def extract_tag_names(tag_type: str) -> list[str]:
        return [t["name"] for t in tags if t.get("type") == tag_type]

    # Build the metadata dictionary
    meta = {
        "id": doujin_id,
        "title": data.get("title", {}).get("pretty"),
        "title_en": data.get("title", {}).get("english"),
        "title_jp": data.get("title", {}).get("japanese"),
        "author": extract_tag_names("artist"),
        "languages": extract_tag_names("language"),
        "tags": extract_tag_names("tag"),
        "scanlator": data.get("scanlator"),
        "group": extract_tag_names("group"),
        "category": extract_tag_names("category"),
        "characters": extract_tag_names("characters"),
        "num_pages": data.get("num_pages"),
        "Publisher": "NHentai.net",
        "web_url": f"{GALLERY_BASE_URL}/{doujin_id}",
        "AgeRating": "mature"
    }

    # Handle upload date and derive year, month, day
    upload_ts = data.get("upload_date")
    if isinstance(upload_ts, int):
        meta["upload_date"] = upload_ts
        dt = datetime.date.fromtimestamp(upload_ts)
        meta.update({"Year": dt.year, "Month": dt.month, "Day": dt.day})

    # Determine if content is Black & White or Manga
    # NHentai uses 'webtoon' tag for color comics
    if any(name.lower() == "webtoon" for name in meta.get("tags", [])):
        meta["BlackAndWhite"] = False
    else:
        meta["Manga"] = True

    # Set primary language code (en or ja)
    langs = [lang.lower() for lang in meta.get("languages", [])]
    if "english" in langs:
        meta["Language"] = "en"
    elif "japanese" in langs:
        meta["Language"] = "ja"

    logger.info(f"Fetched metadata for ID {doujin_id}: {meta}")
    return meta


def get_gallery_url(doujin_id: int) -> str:
    """
    Return the URL to view the doujin in a browser.
    """
    url = f"{GALLERY_BASE_URL}/{doujin_id}"
    logger.info(f"Generated gallery URL for doujin {doujin_id}: {url}")
    return url


if __name__ == '__main__':
    # Quick manual test
    test_id = 1
    result = get_metadata(test_id)
    logger.info(result)
    print(get_gallery_url(test_id))
    print(result)
