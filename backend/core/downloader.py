from typing import List, Optional, Dict
import time
from pathlib import Path
import requests

from backend.utils.logger import logger
from backend.utils.response import respond_progress


def download_images(
    doujin_id: int,
    image_urls: List[str],
    download_dir: str = "downloads",
    retry_errors: int = 0,
    stop=None
) -> Optional[Dict[int, List[Path]]]:
    """
    Download a list of images for a given doujin, reporting progress via SocketIO.

    Args:
        doujin_id: Unique identifier for the doujin.
        image_urls: List of image URLs to download.
        download_dir: Base directory in which to create a subfolder named after the doujin_id.
        retry_errors: Number of additional retry attempts per image if download fails.
        stop: Optional threading.Event to signal cancellation.

    Returns:
        A dict with 'id' and 'paths' of downloaded files, or None if stopped early.
    """
    start_time = time.time()
    total_pages = len(image_urls)
    downloaded_paths: List[Path] = []

    logger.info(f"Starting download for doujin {doujin_id} ({total_pages} pages)")

    # Create target folder if it doesn't exist
    target_folder = Path(download_dir) / str(doujin_id)
    target_folder.mkdir(parents=True, exist_ok=True)

    # Calculate max attempts per image
    max_attempts = retry_errors + 1
    session = requests.Session()

    # Iterate through each URL
    for idx, url in enumerate(image_urls, start=1):
        # Before each image, check if we should stop
        if stop and stop.is_set():
            logger.warning(f"Download stopped at page {idx}/{total_pages}")
            return None

        for attempt in range(1, max_attempts + 1):
            try:
                # Derive file extension and names
                ext = url.split('.')[-1].split('?')[0]
                file_name = f"{doujin_id}_{idx}.{ext}"
                file_path = target_folder / file_name
                webp_path = file_path.with_suffix('.webp')

                # Skip if the file already exists
                if file_path.exists():
                    logger.warning(f"Page {idx}: exists {file_path}, skipping.")
                    downloaded_paths.append(file_path)
                    break
                if webp_path.exists():
                    logger.warning(f"Page {idx}: exists {webp_path}, skipping.")
                    downloaded_paths.append(webp_path)
                    break

                # Download and save
                response = session.get(url)
                response.raise_for_status()
                file_path.write_bytes(response.content)

                logger.info(f"Downloaded page {idx}/{total_pages}: {file_name}")
                downloaded_paths.append(file_path)
                respond_progress('downloads', idx, total_pages)
                break

            except Exception as e:
                logger.error(f"Attempt {attempt}/{max_attempts} failed on page {idx}: {e}")
                if attempt == max_attempts:
                    raise RuntimeError(
                        f"Failed to download page {idx} after {max_attempts} attempts. {e}"
                    )
                time.sleep(0.5)
                logger.info("Retrying...")

    elapsed = time.time() - start_time
    logger.info(
        f"Completed download {doujin_id}: {len(downloaded_paths)}/{total_pages} files in {elapsed:.1f}s"
    )

    return {'id': doujin_id, 'paths': downloaded_paths}

