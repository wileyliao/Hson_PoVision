from paddleocr import PaddleOCR
from OCR_txt_utils import *
from OCR_img_utils import *
from OCR_ui_exactors import *
from Company_Checker import company_checker_main
import cv2
import json


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
        po_num, po_num_conf = po_number_extractor_cht(image_common_text_traditional, "請購單號：")
        expiry_date, expiry_date_conf = expiry_date_extractor_cht(merge_same_row_from_aligned, 'EXPIRY DATE')

    else:
        po_num, po_num_conf = po_number_extractor_en(merge_same_row_from_aligned, 'PONO', processor)
        expiry_date, expiry_date_conf = expiry_date_extractor_en(merge_same_row_from_aligned, 'EXPIRY DATE')

    # 提取產品資訊
    if company == "中外":
        name, name_conf = product_info_extractor_cht_first(merge_same_row_from_aligned, 'PRODUCT')
        if not name:
            en_name = ""
            en_name_conf = 0
            cht_name = ""
            cht_name_conf = 0
        else:
            en_name = name[0]
            en_name_conf = name_conf[0]
            cht_name = name[1]
            cht_name_conf = name_conf[1]

    else:
        name, name_conf = product_info_extractor_en_first(merge_same_row_from_aligned, 'PRODUCT')
        if not name:
            en_name = ""
            en_name_conf = 0
            cht_name = ""
            cht_name_conf = 0
        else:
            en_name = name[0]
            en_name_conf = name_conf[0]
            cht_name = name[1]
            cht_name_conf = name_conf[1]

    qty, qty_conf = quantity_extractor(merge_same_row_from_aligned, 'QUANTITY')

    batch_num, batch_num_conf = batch_num_extractor(merge_same_row_from_aligned, 'BATCH NUMBER')

    result_dict = {
        "po_num": po_num,
        "po_num_conf": po_num_conf,
        "name": en_name,
        "name_conf": en_name_conf,
        "cht_name": cht_name,
        "cht_name_conf": cht_name_conf,
        "qty": qty,
        "qty_conf": qty_conf,
        "batch_num": batch_num,
        "batch_num_conf": batch_num_conf,
        "expirydate": expiry_date,
        "expirydate_conf": expiry_date_conf
    }

    return result_dict


if __name__ == '__main__':
    image_p = './test/01.jpg'
    # image_p = 'output_image.png'
    image = cv2.imread(image_p)
    print(json.dumps(po_vision_main(image), indent=4, ensure_ascii=False))



