from typing import List
from pathlib import Path
from PIL import Image

from backend.utils.logger import logger
from backend.utils.response import respond_progress


def convert_image_to_webp(input_path: Path, quality: int) -> bool:
    """
    Convert a single image file to WebP format and remove the original.

    Args:
        input_path (Path): Path to the source image.
        quality (int): WebP quality (0-100).

    Returns:
        bool: True if conversion succeeded, False otherwise.
    """
    output_path = input_path.with_suffix('.webp')

    # Skip if already converted
    if output_path.exists():
        logger.warning(
            f"[Doujin] Skipping '{input_path.name}': "
            f"'{output_path.name}' already exists."
        )
        return input_path

    try:
        with Image.open(input_path) as img:
            img.save(output_path, format='WEBP', quality=quality)
        input_path.unlink()
        logger.info(
            f"[Doujin] Converted '{input_path.name}' to '{output_path.name}' at quality={quality}."
        )
        return output_path
    except Exception as exc:
        logger.error(f"[Doujin] Failed to convert '{input_path.name}': {exc}")
        return input_path


def convert_images_to_webp(
    doujin_id: int,
    image_paths: List[Path],
    quality: int = 85,
    stop=None
) -> list:
    """
    Batch convert a list of images for a specific doujin to WebP format.

    Args:
        doujin_id (int): Unique identifier of the doujin.
        image_paths (List[Path]): Paths to the image files to convert.
        quality (int): Compression quality for WebP (0-100).

    Returns:
        int: Number of images successfully converted.
    """
    logger.info(f"Starting WebP conversion for doujin {doujin_id}: {len(image_paths)} images.")
    converted_count = 0

    num_pages = image_paths.__len__()
    for i, img_path in enumerate(image_paths, start=0):
        if not img_path.exists():
            logger.warning(
                f"[Doujin {doujin_id}] File not found, skipping: {img_path.name}"
            )
            continue
        path = convert_image_to_webp(img_path, quality)
        if path:
            converted_count += 1
            image_paths[i] = path
        respond_progress('conversion',i+1,num_pages)
        if stop and stop.is_set():
            logger.warning("[conversion] Stopped function")
            return None

    logger.info(
        f"[Doujin] Conversion complete for {doujin_id}: "
        f"{converted_count}/{len(image_paths)} files converted at quality={quality}."
    )
    return image_paths


if __name__ == '__main__':
    # Example usage
    test_id = 1
    folder = Path('downloads') / str(test_id)
    # Collect all images in the folder
    paths = list(folder.glob(f"{test_id}_*.*"))
    count = convert_images_to_webp(test_id, paths, quality=90)
    logger.info(f"Total converted in test run: {count}")
