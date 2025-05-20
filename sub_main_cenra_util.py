import logging
import re

# PO 號格式：10碼 + dash + 2碼
po_pattern = re.compile(r"\d{10}[-–—‐‑‒‾−]?\d{2}")

def extract_po_num(text_list):
    try:
        for item in text_list:
            raw = item["text"]
            cleaned = raw.replace(" ", "").replace("：", ":")
            match = po_pattern.search(cleaned)
            if match:
                return match.group(), item["conf"], item["coord"]
        return "", 0, [[0, 0]] * 4
    except Exception as e:
        logging.error(f'po_number fail: {e}')
        return "", 0, [[0, 0]] * 4

def extract_expiry_dates(text_dict):
    try:
        expiry_data = text_dict.get("EXPIRY DATE", [])
        result = []
        for item in expiry_data:
            text = item['text'].replace(" ", "").replace("：", ":")
            text = re.sub(r"^效期[:：]?", "", text)  # 去掉前綴
            match = re.search(r"\d{4}/\d{2}/\d{2}|\d{8}", text)
            if match:
                expiry = match.group()
                if len(expiry) == 8 and "/" not in expiry:
                    expiry = f"{expiry[:4]}/{expiry[4:6]}/{expiry[6:]}"
                result.append((expiry, item['conf'], item['coord']))
        return result
    except Exception as e:
        logging.error(f'expiry_date fail: {e}')
        return []

def extract_batch_nums(text_dict):
    try:
        batch_data = text_dict.get("BATCH NUMBER", [])
        result = []
        for item in batch_data:
            text = item['text'].replace(" ", "").replace("：", ":").upper()
            text = re.sub(r"^批號[:：]?", "", text)  # 去掉前綴
            # 支援無 dash 版本（如 H2400981）或有 dash（如 K53-0180）
            match = re.search(r"[A-Z]{1}\d{7,}", text) or re.search(r"[A-Z0-9\-]{5,}", text)
            if match:
                result.append((match.group(), item['conf'], item['coord']))
        return result
    except Exception as e:
        logging.error(f'batch_num fail: {e}')
        return []
