import os
import requests, time, glob
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote

from backend.utils.logger import logger

def download_cover(doujin_id: int, out_dir: str = "covers") -> str:
    """
    Download the cover image for a nhentai doujin into out_dir,
    saving it as 'cover<doujin_id>.<ext>'.

    Args:
        doujin_id: the numeric ID of the doujin, e.g. 123456
        out_dir:   local folder to save the cover into (default: 'cover')

    Returns:
        The local file path of the downloaded cover image.

    Raises:
        Exception if the page cannot be fetched or the cover URL not found.
    """

    # Check if cover was already downloaded
    matches = glob.glob(f"{out_dir}/cover_{doujin_id}.*")
    if matches:
        return matches[0]

    # 1) Fetch the gallery page
    page_url = f"https://nhentai.net/g/{doujin_id}/"
    
    for attempt in range(1, 3):
        try:
            resp = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Attempt {attempt}/{3} failed for cover: {e}")
            if attempt == 3:
                raise Exception(f"Failed to download cover after {3} attempts.")
            time.sleep(0.5)
            logger.info("Retrying...")

    # 2) Parse out the og:image meta tag
    soup = BeautifulSoup(resp.text, "html.parser")
    meta = soup.find("meta", property="og:image")
    if not meta or not meta.get("content"):
        raise Exception("Cover URL not found in page metadata")

    cover_url = meta["content"]

    # 3) Determine file extension from the URL path
    path = urlparse(cover_url).path              # e.g. '/galleries/1234/cover.jpg'
    ext = os.path.splitext(unquote(path))[1]     # e.g. '.jpg'
    if not ext:
        ext = ".jpg"  # fallback

    # 4) Build our output filename and path
    os.makedirs(out_dir, exist_ok=True)
    filename = f"cover_{doujin_id}{ext}"           # e.g. 'cover123456.jpg'
    local_path = os.path.join(out_dir, filename)

    # 5) Download the image bytes
    img_resp = requests.get(cover_url, headers={"User-Agent": "Mozilla/5.0"})
    img_resp.raise_for_status()
    with open(local_path, "wb") as f:
        f.write(img_resp.content)

    print(f"Cover saved to {local_path}")
    return local_path

# Example usage:
if __name__ == "__main__":
    downloaded_file = download_cover(1)
    print("Downloaded cover file:", downloaded_file)
