from paddleocr import PaddleOCR
from OCR_txt_utils import *
from OCR_img_utils import *
from Company_Checker import company_checker_main
import logging
import cv2
from OCR_UI_Text import process_ui_result

keyword_en = [
    "PONO",
    "PRODUCT",
    "QUANTITY",
    "BATCH NUMBER",
    "EXPIRY DATE"
]

keyword_cht = [
    "請購單號",
    "規格",
    "數量",
    "批號",
    "效期"
]


def txt_extract(img, reader):
    results = reader.ocr(img, cls=True)
    extracted_data = []
    for bbox, (text, score) in results[0]:
        extracted_data.append({
            "text": text,
            "coord": bbox,
            "conf": score
        })
    return extracted_data


def po_vision_main(image_path):

    # Initial OCR reader and text processor
    ocr_reader = PaddleOCR(use_angle_cls=True, lang='ch')
    processor = TextProcessor()

    # image processing
    image = cv2.imread(image_path)
    image_height, image_width, _ = image.shape

    # Check Company Info
    company = company_checker_main(image, ocr_reader, processor)

    # Decision language usage
    if company == "大昌":
        image_cht = cut_roi_by_ratio(image, 0.15, 0.4)
        image_cht_text = txt_extract(image_cht, ocr_reader)
        image_cht_text_traditional = processor.convert_to_traditional(image_cht_text)

        find_keywords_column = match_keywords(keyword_cht, image_cht_text_traditional, processor)
        print(find_keywords_column)
        aligned_same_column = group_same_column_by_keywords(find_keywords_column, image_cht_text_traditional)
        print(aligned_same_column)

        print(batch_num_checker(aligned_same_column, "批號"))

        return

    else:
        image_common = cut_roi_by_ratio(image, 0.2, 0.4)
        image_common_text = txt_extract(image_common, ocr_reader)
        image_common_text_traditional = processor.convert_to_traditional(image_common_text)
        print(image_common_text_traditional)
        find_keywords_column = match_keywords(keyword_en, image_common_text_traditional, processor)
        # print(find_keywords_column)
        aligned_same_column = group_same_column_by_keywords(find_keywords_column, image_common_text_traditional)
        print(aligned_same_column)

        print(batch_num_checker(aligned_same_column, 'BATCH NUMBER'))

        return



if __name__ == '__main__':
    print(po_vision_main('./test/05.jpg'))
    # print(po_vision_main('./test/01.jpg', keyword_cht))


