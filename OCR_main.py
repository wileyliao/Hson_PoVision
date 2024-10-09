from paddleocr import PaddleOCR
from OCR_txt_utils import TextProcessor, match_keywords, group_same_column_by_keywords
from OCR_UI_Text import process_ui_result
from DKSH_ROI_Extractor import (
    dksh_extract_roi_product,
    dksh_extract_roi_quantity,
    dksh_extract_roi_batch_num,
    dksh_extract_roi_date
)
import logging
import cv2


def extract_coord_from_dict(data, keyword):
    """根據 keyword 從字典中提取 coord"""
    for item in data:
        if keyword in item['text']:
            return item['coord']
    return None


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


def po_vision_main(image_path, keywords, pharma_company_set):
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

    # Initial OCR reader and text processor
    ocr_reader = PaddleOCR(use_angle_cls=True, lang='ch')
    processor = TextProcessor()

    image = cv2.imread(image_path)
    image_height, image_width, _ = image.shape

    # Get original text and convert to traditional
    ori_txt = txt_extract(image_path, ocr_reader)
    logging.info(f'Original text: {ori_txt}')
    ori_traditional_txt = processor.convert_to_traditional(ori_txt)
    print(f'\n {ori_traditional_txt}')

    # Get the company of the PO
    pharma_company = find_company_in_top_n(ori_traditional_txt, top_n=5, pharma_company_set=pharma_company_set)
    logging.info(f'Company: {pharma_company}')
    print(f'\n {pharma_company}')

    if pharma_company == '大昌':

        # 從字典中提取座標
        coord_quantity = extract_coord_from_dict(ori_traditional_txt, '數量')  # 提取 '數量' 的座標
        coord_price = extract_coord_from_dict(ori_traditional_txt, '單價')  # 提取 '單價' 的座標
        coord_product = extract_coord_from_dict(ori_traditional_txt, '品名及規格')  # 提取 '品名及規格' 的座標
        coord_batch_num = extract_coord_from_dict(ori_traditional_txt, '型號/批號')  # 提取 '型號/批號' 的座標
        coord_expiry = extract_coord_from_dict(ori_traditional_txt, '有效期')  # 提取 '有效期' 的座標

        # 提取 product 的 ROI
        roi_product = dksh_extract_roi_product(image, coord_quantity, coord_product, image_height, text_height_multiplier=6)

        # 提取 quantity 的 ROI
        roi_quantity = dksh_extract_roi_quantity(image, coord_quantity, coord_price, text_height_multiplier=6)

        # 提取 batch_num 的 ROI
        roi_batch_num = dksh_extract_roi_batch_num(image, coord_batch_num, text_height_multiplier=6)

        # 提取 date 的 ROI
        roi_date = dksh_extract_roi_date(image, coord_batch_num, coord_expiry, text_height_multiplier=6)

        product_roi_txt = txt_extract(roi_product, ocr_reader)
        quantity_roi_txt = txt_extract(roi_quantity, ocr_reader)
        batch_num_roi_txt = txt_extract(roi_batch_num, ocr_reader)
        expiry_date_roi_txt = txt_extract(roi_date, ocr_reader)

        en_product_txt = product_roi_txt[0]['text']
        en_product_txt_conf = product_roi_txt[0]['conf']

        cht_product_txt = product_roi_txt[1]['text']
        cht_product_txt_conf = product_roi_txt[1]['conf']

        quantity_txt = quantity_roi_txt[0]['text']
        quantity_txt_conf = quantity_roi_txt[0]['conf']

        batch_num_txt = batch_num_roi_txt[0]['text']
        batch_num_txt_conf = batch_num_roi_txt[0]['conf']

        expiry_date_txt = expiry_date_roi_txt[1]['text']
        expiry_date_txt_conf = expiry_date_roi_txt[1]['conf']

        print('en_product_txt')
        print(en_product_txt)
        print(en_product_txt_conf)

        print('cht_product_txt')
        print(cht_product_txt)
        print(cht_product_txt_conf)

        print('quantity_txt')
        print(quantity_txt)
        print(quantity_txt_conf)

        print('batch_num_txt')
        print(batch_num_txt)
        print(batch_num_txt_conf)

        print('expiry_date_txt')
        print(expiry_date_txt)
        print(expiry_date_txt_conf)




        # print(f'po_number: {po_number}')
        # print(f'po_number_conf: {po_number_conf}')
        # print(f'product: {product_roi_txt}， \n {len(product_roi_txt)}')
        # print(f'quantity: {quantity_roi_txt}， \n {len(quantity_roi_txt)}')
        # print(f'batch_num: {batch_num_roi_txt}， \n {len(batch_num_roi_txt)}')
        # print(f'expiry_date: {expiry_date_roi_txt}， \n {len(expiry_date_roi_txt)}')

    else:
        return


if __name__ == '__main__':
    keyword = [
        "PONO",
        "PRODUCT",
        "QUANTITY",
        "BATCH NUMBER",
        "EXPIRYDATE"
    ]

    company_set = {'大昌', '裕利', '和安', '中外'}

    po_vision_main('01_DaChan.jpg', keyword, company_set)


