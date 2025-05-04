
from backend.utils.logger import logger

import xml.etree.ElementTree as ET
from io import BytesIO


def create_ComicInfo(meta: dict):

    logger.info("Converting metadata into ComicInfo.xml format.")

    comic_info = ET.Element("ComicInfo")

    # Map JSON keys to ComicInfo.xml tags (you can expand this)
    field_map = {
        "title": "Title",
        "author": "Artist",
        "tags": "Genre",
        "Language": "LanguageISO",
        "summary": "Summary",
        "id": "Number",
        "Year" : "Year",
        "Month" : "Month",
        "Day" : "Day",
        "scanlator" : "Translator",
        "group" : "Editor",
        "categories" : "Tags",
        "web" : "Web",
        "Publisher" : "Publisher",
        "AgeRating" : "AgeRating",
        "Characters" : "Characters",
        "BlackAndWhite" : "BlackAndWhite",
        "Manga" : "Manga",

    }
    for json_key, xml_tag in field_map.items():
        value = meta.get(json_key)
        if value:
            if isinstance(value, list):
                value = ", ".join(value)
            element = ET.SubElement(comic_info, xml_tag)
            element.text = str(value)

    
    # Convert XML tree to bytes (in memory)
    xml_bytes = BytesIO()
    tree = ET.ElementTree(comic_info)

    # Generate the XML tree and write it to file
    tree = ET.ElementTree(comic_info)
    tree.write(xml_bytes, encoding="utf-8", xml_declaration=True)
    xml_bytes.seek(0)

    return xml_bytes
