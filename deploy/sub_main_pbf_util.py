import re
import logging

def extract_po_num_pbf(text_info):
    try:
        # 改回只支援格式：1140422003-10（10碼-2碼）
        pattern = re.compile(r"\d{10}-\d{2}")

        for item in text_info:
            text = item["text"]
            match = pattern.search(text)
            if match:
                return match.group(), item["conf"], item["coord"]

        return "", 0, [[0, 0]] * 4

    except Exception as e:
        logging.error(f"[寶齡富錦 PBF] PO擷取錯誤: {e}")
        return "", 0, [[0, 0]] * 4



def extract_batch_and_expiry_pbf(text_info):
    try:
        # 批號如 2107-2459 或 397-2402 或 2038-24116
        pattern_batch = re.compile(r"\d{3,4}-\d{3,5}")
        # 效期如 2026/12/27
        pattern_expiry = re.compile(r"\d{4}/\d{2}/\d{2}")

        batch_result = ("", 0, [[0, 0]] * 4)
        expiry_result = ("", 0, [[0, 0]] * 4)

        for item in text_info:
            text = item["text"]

            if batch_match := pattern_batch.search(text):
                batch_result = (batch_match.group(), item["conf"], item["coord"])

            if expiry_match := pattern_expiry.search(text):
                expiry_result = (expiry_match.group(), item["conf"], item["coord"])

        return batch_result, expiry_result

    except Exception as e:
        logging.error(f"[寶齡富錦 PBF] 批號與效期擷取錯誤: {e}")
        return (
            ("", 0, [[0, 0]] * 4),
            ("", 0, [[0, 0]] * 4)
        )
