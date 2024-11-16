from paddleocr import PaddleOCR
from OCR_txt_utils import *
from OCR_img_utils import *
from OCR_ui_exactors import *
from Company_Checker import company_checker_main
import cv2
import json
import logging


keyword_mapping_dict = {
    "PONO": {
        "keywords": ["PONO", "請購單號"]
    },
    "PRODUCT": {
        "keywords": ["PRODUCT", "規格"]
    },
    "QUANTITY": {
        "keywords": ["QUANTITY", "數量"]
    },
    "BATCH NUMBER": {
        "keywords": ["BATCH NUMBER", "型號", "批號"]
    },
    "EXPIRY DATE": {
        "keywords": ["EXPIRY DATE", "EXPIRY", "效期"]
    }
}


def po_vision_main(image_path):

    # Initial OCR reader and text processor
    ocr_reader = PaddleOCR(use_angle_cls=True, lang='ch')
    processor = TextProcessor()

    # image processing
    image_height, image_width, _ = image_path.shape

    # Check Company Info
    company = company_checker_main(image_path, ocr_reader, processor)

    image_common = cut_roi_by_ratio(image_path, 0.2, 0.4)
    image_common_text_traditional = processor.convert_to_traditional(txt_extract(image_common, ocr_reader))

    get_keyword_in_image = match_keywords(keyword_mapping_dict, image_common_text_traditional, processor)

    aligned_same_column = group_same_column_by_keywords(get_keyword_in_image, image_common_text_traditional)
    merge_same_row_from_aligned = merge_same_row(aligned_same_column)

    # 提取請購單號
    if company == "大昌":
        po_num, po_num_conf, po_num_coord = po_number_extractor_cht(image_common_text_traditional, "請購單號：")
        print("請購單號", po_num_coord)

        expiry_date, expiry_date_conf, expiry_date_coord = expiry_date_extractor_cht(merge_same_row_from_aligned, 'EXPIRY DATE')
        print("效期", expiry_date_coord)
    else:
        po_num, po_num_conf, po_num_coord = po_number_extractor_en(merge_same_row_from_aligned, 'PONO', processor)
        print("請購單號", po_num_coord)

        expiry_date, expiry_date_conf, expiry_date_coord = expiry_date_extractor_en(merge_same_row_from_aligned, 'EXPIRY DATE')
        print("效期", expiry_date_coord)

    # 提取產品資訊
    if company == "中外":
        name, name_conf, name_coord = product_info_extractor_cht_first(merge_same_row_from_aligned, 'PRODUCT')
        if not name:
            en_name = ""
            en_name_conf = 0
            en_name_coord = f'0,0;0,0;0,0;0,0'
            cht_name = ""
            cht_name_conf = 0
            cht_name_coord = f'0,0;0,0;0,0;0,0'
        else:
            en_name = name[0]
            en_name_conf = name_conf[0]
            en_name_coord = name_coord[0]
            print("en Name", en_name_coord)

            cht_name = name[1]
            cht_name_conf = name_conf[1]
            cht_name_coord = name_coord[1]
            print("cht Name", cht_name_coord)

    else:
        name, name_conf, name_coord = product_info_extractor_en_first(merge_same_row_from_aligned, 'PRODUCT')
        if not name:
            en_name = ""
            en_name_conf = 0
            en_name_coord = f'0,0;0,0;0,0;0,0'

            cht_name = ""
            cht_name_conf = 0
            cht_name_coord = f'0,0;0,0;0,0;0,0'
        else:
            en_name = name[0]
            en_name_conf = name_conf[0]
            en_name_coord = name_coord[0]
            print("en Name", en_name_coord)

            cht_name = name[1]
            cht_name_conf = name_conf[1]
            cht_name_coord = name_coord[1]
            print("cht Name", cht_name_coord)

    # 提取數量
    qty, qty_conf, qty_coord = quantity_extractor(merge_same_row_from_aligned, 'QUANTITY')
    print("數量", qty_coord)
    # 提取批號
    batch_num, batch_num_conf, batch_num_coord = batch_num_extractor(merge_same_row_from_aligned, 'BATCH NUMBER')
    print("批號", batch_num_coord)

    result_dict = {
        "po_num": po_num,
        "po_num_conf": po_num_conf,
        "po_num_coord": ";".join([f"{int(x)},{int(y)}" for x, y in po_num_coord]),

        "name": en_name,
        "name_conf": en_name_conf,
        "name_coord": ";".join([f"{int(x)},{int(y)}" for x, y in en_name_coord]),

        "cht_name": cht_name,
        "cht_name_conf": cht_name_conf,
        "cht_name_coord": ";".join([f"{int(x)},{int(y)}" for x, y in cht_name_coord]),

        "qty": qty,
        "qty_conf": qty_conf,
        "qty_coord": ";".join([f"{int(x)},{int(y)}" for x, y in qty_coord]),

        "batch_num": batch_num,
        "batch_num_conf": batch_num_conf,
        "batch_num_coord": ";".join([f"{int(x)},{int(y)}" for x, y in batch_num_coord]),

        "expirydate": expiry_date,
        "expirydate_conf": expiry_date_conf,
        "expirydate_coord": ";".join([f"{int(x)},{int(y)}" for x, y in expiry_date_coord])
    }

    logging.info("Result done")
    return result_dict


if __name__ == '__main__':
    image_p = './test/01.jpg'
    # image_p = 'output_image.png'
    image = cv2.imread(image_p)
    print(json.dumps(po_vision_main(image), indent=4, ensure_ascii=False))



