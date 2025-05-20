import logging
from OCR_ui_exactors import po_number_extractor_en, expiry_date_extractor_en, batch_num_extractor
from OCR_txt_utils import TextProcessor

def extract_po_num(text_dict):
    try:
        processor = TextProcessor()
        return po_number_extractor_en(text_dict, "PONO", processor)
    except (KeyError, IndexError, ValueError) as e:
        logging.error(f'po_number fail: {e}')
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]

def extract_expiry_date(text_dict):
    try:
        return expiry_date_extractor_en(text_dict, "EXPIRY DATE")
    except (KeyError, IndexError, ValueError) as e:
        logging.error(f'expiry_date fail: {e}')
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]

def extract_batch_num(text_dict, expiry_coord):
    try:
        return batch_num_extractor(text_dict, "BATCH NUMBER")
    except (KeyError, IndexError, ValueError) as e:
        logging.error(f'batch_num fail: {e}')
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]
