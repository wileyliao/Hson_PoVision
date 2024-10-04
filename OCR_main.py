from paddleocr import PaddleOCR
from OCR_txt_utils import TextProcessor, match_keywords, group_same_column_by_keywords
from OCR_UI_Text import process_ui_result
from extract_ROI_DKSH import (
    dk_extract_roi_product,
    dk_extract_roi_quantity,
    dk_extract_roi_batch_num,
    dk_extract_roi_date
)
import logging
import cv2


def extract_coord_from_dict(data, keyword):
    """根據 keyword 從字典中提取 coord"""
    for item in data:
        if keyword in item['text']:
            return item['coord']
    return None


def find_related_value(data, keyword):
    keyword_coords = None
    target_text = None
    target_conf = None

    # 找到 keyword 的座標
    for item in data:
        if keyword in item['text']:
            keyword_coords = item['coord']
            break

    if not keyword_coords:
        return None  # 如果沒找到關鍵字，返回 None

    # keyword 的右側 X 坐標
    keyword_x_max = max(point[0] for point in keyword_coords)  # 取右邊界 X 坐標
    keyword_y_min = min(point[1] for point in keyword_coords)  # 取上邊界 Y 坐標
    keyword_y_max = max(point[1] for point in keyword_coords)  # 取下邊界 Y 坐標

    # 遍歷所有項目，找到位於 "請購單號" 右側且在同一排的項目
    for item in data:
        item_coords = item['coord']
        item_x_min = min(point[0] for point in item_coords)  # 取左邊界 X 坐標
        item_y_min = min(point[1] for point in item_coords)  # 取上邊界 Y 坐標
        item_y_max = max(point[1] for point in item_coords)  # 取下邊界 Y 坐標

        # 檢查是否在 "請購單號" 的右側並且在同一排
        if item_x_min > keyword_x_max and abs(item_y_min - keyword_y_min) < 10 and abs(item_y_max - keyword_y_max) < 10:
            target_text = item['text']
            target_conf = item['conf']
            break

    return target_text, target_conf


def get_image_left_edge(image):
    return [[0, 0]]  # 左側邊界的坐標


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

    ocr_reader = PaddleOCR(use_angle_cls=True, lang='ch')

    processor = TextProcessor()

    image = cv2.imread(image_path)
    image_height, image_width, _ = image.shape

    ori_txt = txt_extract(image_path, ocr_reader)
    logging.info(f'Original text: {ori_txt}')
    print(f'\n {ori_txt}')

    ori_traditional_txt = processor.convert_to_traditional(ori_txt)
    print(f'\n {ori_traditional_txt}')

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
        roi_product = dk_extract_roi_product(image, coord_quantity, coord_product, image_height, text_height_multiplier=6)

        # 提取 quantity 的 ROI
        roi_quantity = dk_extract_roi_quantity(image, coord_quantity, coord_price, text_height_multiplier=6)

        # 提取 batch_num 的 ROI
        roi_batch_num = dk_extract_roi_batch_num(image, coord_batch_num, text_height_multiplier=6)

        # 提取 date 的 ROI
        roi_date = dk_extract_roi_date(image, coord_batch_num, coord_expiry, text_height_multiplier=6)

        product_txt = txt_extract(roi_product, ocr_reader)
        quantity_txt = txt_extract(roi_quantity, ocr_reader)
        batch_num_txt = txt_extract(roi_batch_num, ocr_reader)
        expiry_date_txt = txt_extract(roi_date, ocr_reader)
        # 提取po_number
        po_number, po_number_conf = find_related_value(ori_traditional_txt, '請購單號')

        print(f'po_number: {po_number}')
        print(f'po_number_conf: {po_number_conf}')
        print(f'product: {product_txt}')
        print(f'quantity: {quantity_txt}')
        print(f'batch_num: {batch_num_txt}')
        print(f'expiry_date: {expiry_date_txt}')

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


