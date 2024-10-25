from paddleocr import PaddleOCR
from OCR_txt_utils import *
from OCR_img_utils import *
from OCR_ui_exactors import *
from Company_Checker import company_checker_main
import logging
import cv2
from OCR_UI_Text import process_ui_result
import json


keyword_mapping_dict = {
    "PONO": {
        "keywords": ["PONO", "請購單號"],
        "extractor": po_number_extractor_en
    },
    "PRODUCT": {
        "keywords": ["PRODUCT", "規格"],
        "extractor": product_info_extractor
    },
    "QUANTITY": {
        "keywords": ["QUANTITY", "數量"],
        "extractor": quantity_extractor
    },
    "BATCH NUMBER": {
        "keywords": ["BATCH NUMBER", "批號"],
        "extractor": batch_num_extractor
    },
    "EXPIRY DATE": {
        "keywords": ["EXPIRY DATE", "EXPIRY", "效期"],
        "extractor": expiry_date_extractor
    }
}



def po_vision_main(image_path):

    # Initial OCR reader and text processor
    ocr_reader = PaddleOCR(use_angle_cls=True, lang='ch')
    processor = TextProcessor()

    # image processing
    image = cv2.imread(image_path)
    image_height, image_width, _ = image.shape

    # Check Company Info
    company = company_checker_main(image, ocr_reader, processor)

    image_common = cut_roi_by_ratio(image, 0.2, 0.4)
    image_common_text_traditional = processor.convert_to_traditional(txt_extract(image_common, ocr_reader))

    get_keyword_in_image = match_keywords(keyword_mapping_dict, image_common_text_traditional, processor)

    aligned_same_column = group_same_column_by_keywords(get_keyword_in_image, image_common_text_traditional)

    print(po_number_extractor_en(aligned_same_column, 'PONO', processor))

    print('規格')
    print(product_info_extractor(aligned_same_column, 'PRODUCT'))

    print('數量')
    print(quantity_extractor(aligned_same_column, 'QUANTITY'))

    print('批號')
    print(batch_num_extractor(aligned_same_column, 'BATCH NUMBER', processor))

    print('效期')
    print(expiry_date_extractor(aligned_same_column, 'EXPIRY DATE'))

    return



if __name__ == '__main__':
    print(po_vision_main('./test/11.jpg'))
    # print(po_vision_main('./test/01.jpg', keyword_cht))


