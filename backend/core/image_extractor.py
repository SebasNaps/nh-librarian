from typing import List, Optional
import requests, time
from bs4 import BeautifulSoup

from backend.utils.logger import logger
from backend.utils.response import respond_progress

# URL templates for API and gallery page access\ nAPI_URL_TEMPLATE = 'https://nhentai.net/api/gallery/{doujin_id}'
PAGE_URL_TEMPLATE = 'https://nhentai.net/g/{doujin_id}/{page}'
API_URL_TEMPLATE = 'https://nhentai.net/api/gallery/{doujin_id}'


def extract_image_urls(
        doujin_id: int,
        retry_errors: int = 0,
        stop=None
        ) -> Optional[List[str]]:
    """
    Retrieve all image URLs for a given doujin ID from nhentai.

    Args:
        doujin_id (int): The ID of the doujin to fetch.

    Returns:
        Optional[List[str]]: List of image URLs or None if API request failed.

    Raises:
        Exception: If unable to parse pages or find images after retries.
    """

    # Fetch metadata from API
    api_url = API_URL_TEMPLATE.format(doujin_id=doujin_id)
    response = requests.get(api_url)
    if response.status_code != 200:
        logger.error(f"Failed to reach ID {doujin_id}: HTTP {response.status_code}.")
        return None

    data = response.json()
    num_pages = data.get('num_pages', 0)

    # Validate page count
    if num_pages > 0:
        logger.info(f"Doujin {doujin_id}: Found {num_pages} pages.")
    else:
        msg = f"Invalid page count for ID {doujin_id}: {num_pages}."
        logger.error(msg)
        raise Exception(msg)

    # Determine retry attempts
    max_attempts = retry_errors + 1

    session = requests.Session()
    image_urls: List[str] = []

    # Iterate through each page and extract the image source
    for page in range(1, num_pages + 1):
        success = False
        for attempt in range(1, max_attempts + 1):
            try:
                page_url = PAGE_URL_TEMPLATE.format(doujin_id=doujin_id, page=page)
                resp = session.get(page_url)
                resp.raise_for_status()

                soup = BeautifulSoup(resp.text, 'html.parser')
                img_container = soup.find(id='image-container')
                img_tag = img_container and img_container.img

                if not img_tag or 'src' not in img_tag.attrs:
                    raise ValueError(f"Missing image on page {page}.")

                src = img_tag['src']
                image_urls.append(src)
                logger.info(f"Page {page}/{num_pages}: Retrieved URL.")
                success = True

                
                respond_progress('urls',page,num_pages)
                if stop and stop.is_set():
                    logger.warning("[urls] Stopped function")
                    return None
                break

            except Exception as exc:
                logger.error(f"Attempt {attempt}/{max_attempts} failed for page {page}: {exc}")
                if attempt == max_attempts:
                    return None
                time.sleep(0.5)
                logger.info("Retrying...")
                # Optionally implement backoff here

        if not success:
            # Should never reach here due to exception on final attempt
            raise Exception(f"Failed to retrieve page {page} after {max_attempts} attempts.")

    return {'id': doujin_id, 'urls': image_urls}


if __name__ == '__main__':
    # Example usage
    test_id = 1
    result = extract_image_urls(test_id)
    print(result['id'])
    if result['urls'] is not None:
        for url in result['urls']:
            print(url)
    else:
        logger.error(f"No images found for doujin ID {test_id}.")
