from DKSH_ROI_Extractor import (
    dksh_extract_roi_product,
    dksh_extract_roi_quantity,
    dksh_extract_roi_batch_num,
    dksh_extract_roi_date
)


def get_po_num(data, keyword):
    keyword_coords = None
    po_num = None
    po_num_conf = None

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
            po_num = item['text']
            po_num_conf = item['conf']
            break

    return po_num, po_num_conf


def extract_keywords_coord_from_dict(data, keyword):
    """根據 keyword 從字典中提取 coord"""
    for item in data:
        if keyword in item['text']:
            return item['coord']
    return None


def dksh_text_extractor_main(ori_traditional_txt, image, image_height, txt_extract, ocr_reader):

    # 從字典中提取座標
    coord_quantity = extract_keywords_coord_from_dict(ori_traditional_txt, '數量')  # 提取 '數量' 的座標
    coord_price = extract_keywords_coord_from_dict(ori_traditional_txt, '單價')  # 提取 '單價' 的座標
    coord_product = extract_keywords_coord_from_dict(ori_traditional_txt, '品名及規格')  # 提取 '品名及規格' 的座標
    coord_batch_num = extract_keywords_coord_from_dict(ori_traditional_txt, '型號/批號')  # 提取 '型號/批號' 的座標
    coord_expiry = extract_keywords_coord_from_dict(ori_traditional_txt, '有效期')  # 提取 '有效期' 的座標

    # 分別提取 product, quantity, batch number, expiry date 的 ROI
    roi_product = dksh_extract_roi_product(image, coord_quantity, coord_product, image_height, text_height_multiplier=6)
    roi_quantity = dksh_extract_roi_quantity(image, coord_quantity, coord_price, text_height_multiplier=6)
    roi_batch_num = dksh_extract_roi_batch_num(image, coord_batch_num, text_height_multiplier=6)
    roi_date = dksh_extract_roi_date(image, coord_batch_num, coord_expiry, text_height_multiplier=6)

    # 將ROI做二次OCR
    product_txt = txt_extract(roi_product, ocr_reader)
    quantity_txt = txt_extract(roi_quantity, ocr_reader)
    batch_num_txt = txt_extract(roi_batch_num, ocr_reader)
    expiry_date_txt = txt_extract(roi_date, ocr_reader)
    # 提取po_number
    po_number, po_number_conf = get_po_num(ori_traditional_txt, '請購單號')

    print(f'po_number: {po_number}')
    print(f'po_number_conf: {po_number_conf}')
    print(f'product: {product_txt}')
    print(f'quantity: {quantity_txt}')
    print(f'batch_num: {batch_num_txt}')
    print(f'expiry_date: {expiry_date_txt}')