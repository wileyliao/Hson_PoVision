from paddleocr import PaddleOCR
from OCR_txt_utils import TextProcessor
from DKSH_text_extractor import dksh_text_extractor_main
from Common_text_extractor import common_text_extractor_main

import logging
import cv2


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


def find_company_in_top_n(data, top_n=5, pharma_company_set=None):
    pharma_company = None

    for i, item in enumerate(data):
        if i >= top_n:
            break
        # 遍歷集合，檢查集合中的公司名稱是否出現在 item['text'] 中
        for company in pharma_company_set:
            if company in item['text']:
                pharma_company = company  # 返回集合中匹配到的值，而不是 item['text']
                break
        if pharma_company:  # 如果找到了匹配，立即跳出外層迴圈
            break

    return pharma_company


def po_vision_main(image_path, pharma_company_set):

    # Initial OCR reader and text processor
    ocr_reader = PaddleOCR(use_angle_cls=True, lang='ch')
    processor = TextProcessor()

    # image processing
    image = cv2.imread(image_path)
    image_height, image_width, _ = image.shape

    # Get original text and convert to traditional
    ori_txt = txt_extract(image_path, ocr_reader)
    logging.info(f'Original text: {ori_txt}')
    ori_traditional_txt = processor.convert_to_traditional(ori_txt)

    # Get the company of the PO
    pharma_company = find_company_in_top_n(ori_traditional_txt, top_n=5, pharma_company_set=pharma_company_set)
    logging.info(f'Company: {pharma_company}')

    # Determine which Algo will use
    if pharma_company == '大昌':
        result_dict = dksh_text_extractor_main(ori_traditional_txt, image, image_height, txt_extract, ocr_reader)
        logging.info(f'Result :{result_dict}')
        return result_dict

    else:
        common_text_extractor_main(ori_traditional_txt, image, image_height, txt_extract, ocr_reader)
        return


if __name__ == '__main__':
    company_set = {'大昌', '裕利', '和安', '中外'}

    print(po_vision_main('./test/11.jpg', company_set))


