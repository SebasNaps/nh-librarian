
import time
import requests
from bs4 import BeautifulSoup

from backend.utils.logger import logger
from backend.utils.response import respond_progress


# Constants
HEADERS = {'User-Agent': 'Mozilla/5.0'}
NHENTAI_URL = 'https://nhentai.net'


def load_session_cookies(session: dict) -> dict:
    """
    Validate and return the session cookies for authenticated requests.
    Raises:
        ValueError: if required session keys are missing in config.
    """
    if session==None:
        return None
    required_keys = ('cookie_id', 'cookie_cf')
    missing = [k for k in required_keys if not session.get(k)]
    if missing:
        raise ValueError(f"Missing session keys in config: {missing}")
    return {'sessionid': session['cookie_id'], 'cf_clearance': session['cookie_cf']}


def fetch_favorites_page(page: int, cookies: dict, stop) -> tuple[list[dict], bool]:
    """
    Fetch a single favorites page and parse gallery entries.

    Args:
        page: 1-based favorites page number
        cookies: session cookies for the request

    Returns:
        A tuple of (list of favorites, has_next_page flag)
    """
    url = f"{NHENTAI_URL}/favorites/?page={page}"
    resp = requests.get(url, headers=HEADERS, cookies=cookies)

    if resp.status_code != 200:
        logger.error(f"Failed to fetch favorites page {page} (status {resp.status_code})")
        return [], False

    soup = BeautifulSoup(resp.text, 'html.parser')
    gallery_divs = soup.select('.gallery')
    favorites = []

    for div in gallery_divs:
        link = div.find('a', href=True)
        title_div = div.find('div', class_='caption')
        if not link or not title_div:
            continue
        # Extract doujin ID from URL: /g/123456/
        doujin_id = link['href'].strip('/').split('/')[-1]
        title = title_div.get_text(strip=True)
        favorites.append({'id': doujin_id, 'title': title})

        if stop and stop.is_set():
            logger.warning("[favorites] Stopped function")
            return None, None

    # Determine if there's a "next" pagination link
    has_next = bool(soup.select_one('.pagination a.next'))
    return favorites, has_next


def fetch_all_favorites(session: dict, page_limit: int | None = None, stop=None) -> list[dict] | None:
    """
    Retrieve all favorite galleries, up to an optional page limit.
    Saves results to JSON if configured.

    Args:
        page_limit: max number of pages to fetch (None for unlimited)

    Returns:
        List of favorite dicts, or None on error.
    """
    
    logger.info(f"Starting favorites fetch (page_limit={page_limit})")

    try:
        # Test base connectivity
        resp = requests.get(NHENTAI_URL, headers=HEADERS)
        resp.raise_for_status()
    except requests.RequestException as err:
        logger.error(f"Base NHentai unreachable: {err}")
        raise

    # Load and validate session
    try:
        cookies = load_session_cookies(session)
    except ValueError as err:
        logger.error(err)
        return None

    # Iterate through pages
    all_favorites = []
    page = 1
    start = time.time()

    while True:
        logger.info(f"Fetching favorites page {page}")
        page_favs, has_next = fetch_favorites_page(page, cookies, stop=stop)
        if stop and stop.is_set():
            logger.warning("[favorites] Stopped function")
            return None
        
        if not page_favs:
            break
        all_favorites.extend(page_favs)
        if not has_next or (page_limit and page >= page_limit):
            break
        page += 1
        respond_progress('favorites',page,False)
        

    elapsed = time.time() - start
    logger.info(f"Fetched {len(all_favorites)} favorites in {elapsed:.2f}s over {page} pages.")

    respond_progress('favorites',page,True)

    return all_favorites

if __name__ == '__main__':
    # Quick manual test
    test_id = 1
    session = {
        'sessionid': '6cl8ghtoctoghtwchl5ta8ppwa16ssp5',
        'cf_clearance' : '2Ohx5b1xNMgMUFZ5ExbfLmweCXiRACj3'
        }
    result = fetch_all_favorites(session=session, page_limit=1)
    logger.info(result.__len__())
    for res in result:
        print(res)
