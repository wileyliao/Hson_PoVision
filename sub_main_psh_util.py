# sub_main_psh_util.py
import re
import logging

def extract_po_num_psh(text_info):
    try:
        pattern = re.compile(r"\d{10}-\d{2}")
        for item in text_info:
            match = pattern.search(item["text"].replace(" ", ""))
            if match:
                return match.group(), item["conf"], item["coord"]
    except Exception as e:
        logging.error(f'PSH PO number extraction failed: {e}')
    return "", 0, [[0, 0]] * 4

def extract_batch_num_psh(text_info):
    try:
        pattern = re.compile(r"\d{3}-\d{4}")
        for item in text_info:
            match = pattern.search(item["text"].replace(" ", ""))
            if match:
                return match.group(), item["conf"], item["coord"]
    except Exception as e:
        logging.error(f'PSH Batch number extraction failed: {e}')
    return "", 0, [[0, 0]] * 4

def extract_expiry_date_psh(text_info):
    try:
        pattern = re.compile(r"\d{4}\.\d{2}\.\d{2}")
        for item in text_info:
            match = pattern.search(item["text"].replace(" ", ""))
            if match:
                return match.group(), item["conf"], item["coord"]
    except Exception as e:
        logging.error(f'PSH Expiry date extraction failed: {e}')
    return "", 0, [[0, 0]] * 4
