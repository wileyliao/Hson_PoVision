from paddleocr import PaddleOCR
from OCR_txt_utils import *
from OCR_company_checker import company_checker_main
from sub_main_asia import handle_asia
from sub_main_chugai import handle_chugai
from sub_main_dksh import handle_dksh
from sub_main_hoan import handle_hean
from sub_main_nine import handle_nine
from sub_main_yuli import handle_yuli
from sub_main_dls import handle_dls
from sub_main_yonfu import handle_yufu
from sub_main_pingting import handle_pingting
from sub_main_pbf import handle_pbf
from sub_main_dq import handle_dq
from sub_main_cenra import handle_cenra
from sub_main_psh import handle_psh


from PIL import Image
import cv2
import numpy as np
import json
import logging
from functools import reduce
import operator

keyword_mapping_dict = {
    "PONO": {"keywords": ["PONO", "請購單號", "請購", "交貨"]},
    "PRODUCT": {"keywords": ["PRODUCT", "規格", "商品"]},
    "QUANTITY": {"keywords": ["QUANTITY", "數量"]},
    "BATCH NUMBER": {"keywords": ["BATCH NUMBER", "型號", "批號"]},
    "EXPIRY DATE": {"keywords": ["EXPIRY DATE", "EXPIRY", "效期"]}
}

ocr_reader = PaddleOCR(lang='ch', device='gpu:0')
def po_vision_main(image):
    if isinstance(image, str):
        image = cv2.imdecode(np.fromfile(image, dtype=np.uint8), cv2.IMREAD_COLOR)

    processor = TextProcessor()

    # ✅ 用 PIL 開圖（支援中文路徑）
    image_height, image_width, _ = image.shape

    image_common_text_traditional = processor.convert_to_traditional(txt_extract(image, ocr_reader))
    logging.info(f'origin text: {image_common_text_traditional}')
    print(image_common_text_traditional)

    company, direction = company_checker_main(image_common_text_traditional)
    logging.info(f'Company: {company}')

    image_cx = image_width / 2
    box_cx = sum(point[0] for point in direction) / 4
    box_cy = sum(point[1] for point in direction) / 4
    degree = '0'

    # ✅ 使用 PIL 圖片轉 OpenCV 圖片處理旋轉
    if image_height > image_width:
        if box_cx < image_cx:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            degree = '90'
        else:
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            degree = '270'
    elif image_width > image_height and box_cy > image_height / 2:
        image = cv2.rotate(image, cv2.ROTATE_180)
        degree = '180'

    # ✅ 把旋轉後的 cv 圖轉回 PIL 給 OCR 用
    rotated_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    rotated_pil.save("temp_rotated.jpg")  # 暫存檔給 txt_extract()

    image_common_text_traditional = processor.convert_to_traditional(txt_extract("temp_rotated.jpg", ocr_reader))

    get_keyword_in_image = match_keywords(keyword_mapping_dict, image_common_text_traditional, processor)
    logging.info(f"Keywords position: {get_keyword_in_image}")

    aligned_same_column = group_same_column_by_keywords(get_keyword_in_image, image_common_text_traditional)
    logging.info(f"Text in same column: {aligned_same_column}")

    merge_same_row_from_aligned = merge_same_row(aligned_same_column)
    logging.info(f"Merger same row: {merge_same_row_from_aligned}")

    if company == "大昌":
        result = handle_dksh(image_common_text_traditional, merge_same_row_from_aligned)
    elif company == "久裕":
        result = handle_nine(image_common_text_traditional)
    elif company == "亞洲":
        result = handle_asia(merge_same_row_from_aligned)
    elif company == "中外":
        result = handle_chugai(merge_same_row_from_aligned)
    elif company == "裕利":
        result = handle_yuli(merge_same_row_from_aligned)
    elif company == "和安":
        result = handle_hean(merge_same_row_from_aligned)
    elif company == "大隆":
        result = handle_dls(image_common_text_traditional, merge_same_row_from_aligned)
    elif company == "永福":
        result = handle_yufu(image_common_text_traditional, "temp_rotated.jpg", ocr_reader)
    elif company == "平廷":
        result = handle_pingting(image_common_text_traditional, merge_same_row_from_aligned)
    elif company == "齡富":
        result = handle_pbf(image_common_text_traditional, merge_same_row_from_aligned)
    elif company == "登詮":
        result = handle_dq(image_common_text_traditional)
    elif company == "CENRA":
        result= handle_cenra(merge_same_row_from_aligned, image_common_text_traditional)
    elif company == "尚典":
        result = handle_psh(image_common_text_traditional, merge_same_row_from_aligned)

    else:
        result = [{"po_num": ("", 0, [[0, 0]] * 4), "expiry_date": ("", 0, [[0, 0]] * 4),
                  "batch_num": ("", 0, [[0, 0]] * 4)}]

    result=result[0]
    po_num, po_num_conf, po_num_coord = result["po_num"]
    expiry_date, expiry_date_conf, expiry_date_coord = result["expiry_date"]
    batch_num, batch_num_conf, batch_num_coord = result["batch_num"]

    batch_expiry_bool_operator = [1]

    result_dict = {
        "po_num": po_num,
        "po_num_conf": str(po_num_conf),
        "po_num_coord": ";".join([f"{int(x)},{int(y)}" for x, y in po_num_coord]),
        "batch_num": batch_num,
        "batch_num_conf": str(batch_num_conf),
        "batch_num_coord": ";".join([f"{int(x)},{int(y)}" for x, y in batch_num_coord]),
        "expirydate": expiry_date,
        "expirydate_conf": str(expiry_date_conf),
        "expirydate_coord": ";".join([f"{int(x)},{int(y)}" for x, y in expiry_date_coord]),
        "degree": degree
    }
    batch_expiry_bool = reduce(operator.mul, batch_expiry_bool_operator) == 1

    logging.info("Result done")
    return result_dict, str(batch_expiry_bool), degree


if __name__ == '__main__':
    image_p = r"C:\pycharm\po_vision_n\po_vision_img\po_vision\CENRA\CENRA_01.jpg"
    print(json.dumps(po_vision_main(image_p), indent=4, ensure_ascii=False))