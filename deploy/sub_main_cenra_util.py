import re
import logging

# 擷取 PO 單號（固定格式 11碼數字 + dash + 2碼）
def extract_po_num_cenra(text_info):
    pattern = re.compile(r"\d{10}-\d{2}")
    for item in text_info:
        match = pattern.search(item["text"])
        if match:
            return match.group(), item["conf"], item["coord"]
    return "", 0, [[0, 0]] * 4


# 擷取效期（格式 YYYY/MM/DD）
def extract_expiry_date_cenra(text_info):
    pattern = re.compile(r"\d{4}/\d{2}/\d{2}")
    for item in text_info:
        match = pattern.search(item["text"])
        if match:
            return match.group(), item["conf"], item["coord"]
    return "", 0, [[0, 0]] * 4


# 擷取批號（關鍵字 "批號" 開頭）
def extract_batch_num_cenra(text_info):
    for item in text_info:
        text = item["text"].replace(" ", "")
        if text.startswith("批號") or "批號：" in text:
            batch = text.replace("批號", "").replace("：", "").strip()
            if batch:
                return batch, item["conf"], item["coord"]
    return "", 0, [[0, 0]] * 4
