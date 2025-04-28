import logging
from OCR_ui_exactors import expiry_date_extractor_cht, batch_num_extractor_dk
import re

def extract_po_num(text_info):
    try:
        pattern = re.compile(r"\d{10}[-–—‐‑‒‾−]\d{2}")
        for item in text_info:
            clean_text = item["text"].replace(" ", "")
            match = pattern.search(clean_text)
            if match:
                return match.group(0), item["conf"], item["coord"]
        return "", 0, [[0, 0]] * 4
    except Exception as e:
        logging.error(f"PO number extraction failed: {e}")
        return "", 0, [[0, 0]] * 4



def extract_expiry_date(text_dict):
    try:
        return expiry_date_extractor_cht(text_dict, "EXPIRY DATE")
    except (KeyError, IndexError, ValueError) as e:
        logging.error(f'Expiry date extraction failed: {e}')
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]

def extract_batch_num(text_dict):
    try:
        return batch_num_extractor_dk(text_dict, "BATCH NUMBER")
    except (KeyError, IndexError, ValueError) as e:
        logging.error(f'Batch number extraction failed: {e}')
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]
