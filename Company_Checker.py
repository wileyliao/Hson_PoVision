from paddleocr import PaddleOCR
from OCR_txt_utils import TextProcessor
from OCR_img_utils import *

company_set = {'大昌', '裕利', '和安', '中外'}


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


def company_checker_main(image, reader, processor):

    image_company_info = cut_roi_by_ratio(image, 0, 0.15)
    company_txt_origin = txt_extract(image_company_info, reader)
    company_txt_traditional = processor.convert_to_traditional(company_txt_origin)
    pharma_company = find_company_in_top_n(company_txt_traditional, top_n=5, pharma_company_set=company_set)

    return pharma_company


if __name__ == '__main__':
    image_origin = cv2.imread('./test/01.jpg')
    ocr_reader = PaddleOCR(use_angle_cls=True, lang='ch')
    txt_processor = TextProcessor()

    print(company_checker_main(image_origin, ocr_reader, txt_processor))
