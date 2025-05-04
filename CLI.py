
import argparse

from backend.utils.logger import logger
from backend import backend_entry


def main():
    """
    CLI entrypoint: parse arguments, load previous data, dispatch to flows.
    """
    parser = argparse.ArgumentParser("nhentai Archiver Tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--auto", action="store_true", help="Automatic Mode: archives all favorites as .cbz files")
    group.add_argument("-f", "--favorite", action="store_true", help="Archive all favorites")
    # group.add_argument("-l", "--list", dest="list_ids",
    #                    help="Archive a list of doujin by ID (comma-separated or path to file)")
    group.add_argument("-l", "--list", action="store_true",
                       help="Archive a list of doujin using the file 'data/id_list.json'")
    # group.add_argument("-d", "--doujin", type=int, help="Archive a single doujin by ID")

    parser.add_argument("--cbz", action="store_true", help="Create CBZ after download")
    # parser.add_argument("--limit", type=int, default=None, help="Limit items to process")
    parser.add_argument("-r", "--run_until", choices=['f','m','u','d','c'],
                        help="f=fetch favs only, m=metadata, u=urls, d=download")
    args = parser.parse_args()

    # Normalize run_until to integer steps
    STEP_MAP = {'f': 'fav', 'm': 'meta', 'u': 'urls', 'd': 'down', 'c': 'cbz'}
    run_until = STEP_MAP.get(args.run_until) if args.run_until else None
    if args.cbz and run_until=='down':
        run_until='cbz'

    logger.info("----CLI Entry----")
    logger.info(f"Arguments {args}")



    # Dispatch based on CLI flags
    if args.auto:
        backend_entry.start_task()
    elif args.favorite:
        backend_entry.start_task(mode='custom', id_source='favs', run_until=run_until)
    elif args.list:
        backend_entry.start_task(mode='custom', id_source='id_list', run_until=run_until)


if __name__ == '__main__':
    main()
