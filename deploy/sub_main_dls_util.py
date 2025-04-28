import re
import logging

def extract_po_num_dls_from_product_column(structured_data):
    try:
        product_data = structured_data.get("PRODUCT", [])


        # 支援常見破折號，允許空格
        pattern = re.compile(r"\d{10}\s*[-–—‐‑‒‾−]\s*\d{2}")

        for item in product_data:
            raw_text = item["text"]

            match = pattern.search(raw_text)
            if match:
                matched_po = match.group().replace(" ", "")
                return matched_po, item["conf"], item["coord"]

        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]

    except Exception as e:
        logging.error(f'PO number extraction from PRODUCT failed: {e}')
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]




def extract_batch_and_expiry_dls(text_dict):
    try:
        # 抓批號-效期格式，例如：B4L81-20271211（含破折號變體）
        pattern = re.compile(r"([A-Z0-9]{3,})[-–—‐‑‒‾−](\d{8})")

        for item in text_dict:
            text = item["text"].replace(" ", "")
            match = pattern.search(text)
            if match:
                batch = match.group(1)
                expiry = match.group(2)
                return (
                    (batch, item["conf"], item["coord"]),
                    (expiry, item["conf"], item["coord"])
                )

        return (
            ("", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]),
            ("", 0, [[0, 0], [0, 0], [0, 0], [0, 0]])
        )

    except Exception as e:
        logging.error(f'Batch & Expiry extraction failed: {e}')
        return (
            ("", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]),
            ("", 0, [[0, 0], [0, 0], [0, 0], [0, 0]])
        )
