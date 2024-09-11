from paddleocr import PaddleOCR
from OCR_txt_utils import TextProcessor, match_keywords, group_same_column_by_keywords
from OCR_UI_Text import process_ui_result
import logging


def po_vision_main(image_path, keywords):
    def txt_extract(image, reader):
        results = reader.ocr(image, cls=True)
        extracted_data = []
        for bbox, (text, score) in results[0]:
            extracted_data.append({
                "text": text,
                "coord": bbox,
                "conf": score
            })
        return extracted_data

    ocr_reader = PaddleOCR(use_angle_cls=True, lang='ch')

    ori_txt = txt_extract(image_path, ocr_reader)
    logging.info(f'Original text: {ori_txt}')

    processor = TextProcessor()

    matched = match_keywords(keywords, ori_txt, processor)
    logging.info(f'match_keywords: {matched}')

    group = group_same_column_by_keywords(matched, ori_txt)
    logging.info(f'group_same_column_by_keywords: {group}')

    ui_result = process_ui_result(group, processor)
    logging.info(f'process_ui_result: {ui_result}')
    logging.info(f'End analyze')

    return ui_result
