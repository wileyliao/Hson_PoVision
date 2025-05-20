import re
import logging

def extract_po_num_pingting(structured_data):
    try:
        product_data = structured_data.get("PRODUCT", [])

        # e.g., 1140416002-39
        pattern = re.compile(r"\d{10}\s*[-–—‐‑‒‾−]\s*\d{2}")

        for item in product_data:
            raw_text = item["text"]
            match = pattern.search(raw_text)
            if match:
                matched_po = match.group().replace(" ", "")
                return matched_po, item["conf"], item["coord"]

        return "", 0, [[0, 0]] * 4

    except Exception as e:
        logging.error(f'PO number extraction for 平廷 failed: {e}')
        return "", 0, [[0, 0]] * 4


def extract_batch_and_expiry_pingting(text_dict):
    try:
        # batch: 英數字6碼（如 NT5428） expiry: 3位數年/2位月/2位日（025/12/31）
        pattern_batch = re.compile(r"\b([A-Z]{1,2}\d{3,5}|WM\d{4}|\d{6})\b")
        pattern_expiry = re.compile(r"(0\d{2}/\d{2}/\d{2})")

        best_batch = ("", 0, [[0, 0]] * 4)
        best_expiry = ("", 0, [[0, 0]] * 4)

        for item in text_dict:
            text = item["text"].replace(" ", "")

            if batch_match := pattern_batch.search(text):
                batch = batch_match.group(1)
                best_batch = (batch, item["conf"], item["coord"])

            if expiry_match := pattern_expiry.search(text):
                expiry = expiry_match.group(1)
                best_expiry = (expiry, item["conf"], item["coord"])

        return best_batch, best_expiry

    except Exception as e:
        logging.error(f'Batch & Expiry extraction for 平廷 failed: {e}')
        return (
            ("", 0, [[0, 0]] * 4),
            ("", 0, [[0, 0]] * 4)
        )
