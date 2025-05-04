from typing import List, Dict
from pathlib import Path
import zipfile
from natsort import natsorted
import json

from backend.utils.logger import logger
from backend.utils.comic_info import create_ComicInfo

def delete_files(paths: list[Path]) -> int:
    """
    Delete all files in `paths`.
    Returns the number of files successfully deleted.
    """
    deleted = 0
    for p in paths:
        try:
            p.unlink()
            deleted += 1
        except FileNotFoundError:
            # file was already gone—skip
            continue
        except Exception as e:
            logger.error(f"Error deleting {p!s}: {e}")
    return deleted

def create_cbz(
    meta: Dict[str, object],
    image_paths: List[Path],
    cbz_dir: str,
    autodelete_images: bool=False
) -> Path:
    """
    Package a sequence of images and metadata into a CBZ (ZIP) archive.

    Args:
        meta (Dict[str, object]): Metadata dictionary with at least the 'id' field and optional 'title'.
        image_paths (List[Path]): List of image file paths to include in the archive.
        download_dir (str): Base directory where images are stored (unused if image_paths is absolute).
        cbz_dir (str): Target directory where the CBZ will be written.

    Returns:
        Path: Path to the created CBZ file.

    Raises:
        ValueError: If 'id' is missing in metadata.
        FileNotFoundError: If any provided image path does not exist or output directory cannot be created.
    """
    # Validate metadata
    doujin_id = meta.get('id')
    if doujin_id is None:
        raise ValueError("Metadata must contain an 'id' field.")

    # Determine archive filename
    title = meta.get('title', f"doujin_{doujin_id}")
    raw_filename = f"{doujin_id} - {title}.cbz"
    safe_filename = "".join(c for c in raw_filename if c.isalnum() or c in " _-().").rstrip()

    # Prepare output directory
    output_dir = Path(cbz_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"[Doujin {doujin_id}] Failed to create output directory: {output_dir} - {e}")
        raise

    cbz_path = output_dir / safe_filename
    if cbz_path.exists():
        logger.warning(f"[Doujin {doujin_id}] CBZ already exists at {cbz_path}, skipping creation.")
        return cbz_path

    # Ensure all image files exist
    for img in image_paths:
        if not img.exists():
            logger.error(f"[Doujin {doujin_id}] Image file not found: {img}")
            raise FileNotFoundError(f"Image file not found: {img}")

    # Sort images naturally to maintain proper page order
    sorted_images = natsorted(image_paths, key=lambda p: p.name)

    # Generate ComicInfo.xml metadata
    xml_source = create_ComicInfo(meta=meta)
    xml_bytes = xml_source.read() if hasattr(xml_source, 'read') else xml_source

    logger.info(f"[Doujin {doujin_id}] Creating CBZ archive with {len(sorted_images)} images.")

    # Write CBZ archive
    with zipfile.ZipFile(cbz_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for img in sorted_images:
            archive.write(img, arcname=img.name)

        archive.writestr('metadata.json', json.dumps(meta, indent=4))
        archive.writestr('ComicInfo.xml', xml_bytes)

    if autodelete_images:
        logger.info("Deleting raw image files after archiving.")
        deleted = delete_files(image_paths)
        logger.info(f"Deleted {deleted} of {image_paths.__len__()}")


    logger.info(f"[Doujin {doujin_id}] CBZ created at {cbz_path}")
    return cbz_path


if __name__ == '__main__':
    # Example usage
    from pathlib import Path
    test_meta = {'id': 1, 'title': 'Eat The Rich'}
    download_dir = 'downloads'
    cbz_dir = 'archives'
    images = list(Path(download_dir, str(test_meta['id'])).glob(f"{test_meta['id']}_*.*"))
    create_cbz(test_meta, images, cbz_dir)
