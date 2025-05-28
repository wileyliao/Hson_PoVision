import re
import logging
from PIL import Image
from paddleocr import PaddleOCR
import numpy as np

# --- 抓 PO number ---
def extract_po_num_yufu(text_info):
    try:
        pattern = re.compile(r"P/O[:：]?\s*(\d{10}[-–—‐‑‒‾−]\d{2})")
        for item in text_info:
            match = pattern.search(item["text"].replace(" ", ""))
            if match:
                return match.group(1), item["conf"], item["coord"]
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]
    except Exception as e:
        logging.error(f"PO number extraction failed for 永福: {e}")
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]


# --- 抓批號：找 "批號" 關鍵字下方框，並排除前面產品名 ---
def extract_batch_num_yufu(text_info, image_path, ocr_model):
    try:

        # Step 1: 找包含 "英文" 和 "保碼" 的欄位框
        eng_box = next((item for item in text_info if "英文" in item["text"]), None)
        nhicode_box = next((item for item in text_info if "保碼" in item["text"]), None)

        if not eng_box or not nhicode_box:
            print("[DEBUG] 找不到『英文』或『保碼』欄位")
            return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]


        xs = [pt[0] for pt in eng_box["coord"]]
        ys = [pt[1] for pt in eng_box["coord"]]

        x1 = min(xs)
        y_top = min(ys)
        y_bottom = max(ys) + 120

        # 對 nhicode_box 也做同樣處理
        x2 = max([pt[0] for pt in nhicode_box["coord"]])

        x_mid = (x1 + x2) / 2
        x_65 = x1 + (x2 - x1) * 0.65


        print(f"[DEBUG] x1={x1}, x2={x2}, x_mid={x_mid}, x_65={x_65}")
        print(f"[DEBUG] y_top={y_top}, y_bottom={y_bottom}")

        # Step 2: 開啟圖片 & 裁切區域
        image = Image.open(image_path)
        crop_box = (int(x_mid), int(y_top), int(x_65), int(y_bottom))
        offset_x, offset_y = crop_box[0], crop_box[1]
        cropped_image = image.crop(crop_box)

        # cropped_image.show('crop')

        # Step 3: 放大圖片
        zoomed_image = cropped_image.resize(
            (cropped_image.width * 2, cropped_image.height * 2),
            Image.LANCZOS
        )

        scale_x = cropped_image.width / zoomed_image.width
        scale_y = cropped_image.height / zoomed_image.height

        # Step 4: OCR 辨識
        ocr_result = ocr_model.ocr(np.array(zoomed_image))

        print("[DEBUG] OCR 批號區結果：", ocr_result)

        # Step 5: 抓出符合格式的批號（前綴有中文就裁掉再判斷）
        for line in ocr_result[0]:
            raw_text = line[1][0].strip().replace(" ", "")
            cleaned_text = re.sub(r"^[\u4e00-\u9fff]+", "", raw_text)

            # 支援數字或英文字母開頭的批號格式（長度5~8）
            matches = re.findall(r"\b[0-9A-Z]{5,8}\b", cleaned_text)
            if matches:
                best_match = max(matches, key=len)
                print(f"[DEBUG] 命中批號：{best_match}")

                # ❗將小圖座標轉回原圖座標
                new_coords = []
                for x, y in line[0]:
                    orig_x = int(x / scale_x + offset_x)
                    orig_y = int(y / scale_y + offset_y)
                    new_coords.append([orig_x, orig_y])

                return best_match, line[1][1], new_coords

        print("[DEBUG] 找不到符合格式的批號")
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]

    except Exception as e:
        logging.error(f"批號擷取錯誤: {e}")
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]


# --- 抓效期：找"效期"下方框，取前8碼（排除連在一起的健保碼） ---
def extract_expiry_yufu(text_info):
    try:
        keyword = "效期"
        expiry_candidates = []
        keyword_box = None

        for item in text_info:
            if keyword in item["text"]:
                keyword_box = item
                break

        if not keyword_box:
            return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]

        x1, y1 = keyword_box["coord"][0]
        for item in text_info:
            text = item["text"].strip().replace(" ", "")
            if re.match(r"\d{8,}", text) and item["coord"][0][1] > y1:
                expiry_candidates.append(item)

        if expiry_candidates:
            best = sorted(expiry_candidates, key=lambda x: x["coord"][0][1])[0]
            expiry_8 = re.findall(r"\d{8}", best["text"].replace(" ", ""))
            if expiry_8:
                return expiry_8[0], best["conf"], best["coord"]

        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]
    except Exception as e:
        logging.error(f"Expiry date extraction failed for 永福: {e}")
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]
