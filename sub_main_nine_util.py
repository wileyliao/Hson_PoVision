import logging
from OCR_ui_exactors import po_number_extractor_cht, expiry_date_extractor_nine, batch_num_extractor_nine

def extract_po_num(text_dict):
    try:
        return po_number_extractor_cht(text_dict, "交貨")
    except (KeyError, IndexError, ValueError) as e:
        logging.error(f'po_number fail: {e}')
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]

def extract_expiry_date(text_dict):
    try:
        return expiry_date_extractor_nine(text_dict[-10:])
    except (KeyError, IndexError, ValueError) as e:
        logging.error(f'expiry_date fail: {e}')
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]

def extract_batch_num(text_dict, expiry_coord):
    try:
        return batch_num_extractor_nine(text_dict[-10:], expiry_coord)
    except (KeyError, IndexError, ValueError) as e:
        logging.error(f'batch_num fail: {e}')
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]
