from Common_ROI_Extractor import *
import re


def extract_keywords_coord_from_dict(data, keywords):
    """根據 keyword 從字典中提取 coord"""
    match_coords = []
    for item in data:
        item_text = item['text'].replace(" ", "").lower()
        for keyword in keywords:
            if keyword.replace(" ", "").lower() in item_text:
                match_coords.append(item['coord'])
    return match_coords if match_coords else None


def extract_text_conf(txt_extract, roi, idx, ocr_reader):
    txt_data = txt_extract(roi, ocr_reader)
    return txt_data[idx]['text'], txt_data[idx]['conf']


def get_po_num(data):
    # 定義關鍵字（PO/No. 或 P0/No.）
    keywords = ["PO/No.", "P0/No."]

    # 第一步：嘗試使用正則表達式提取 PO/No. 後面的數字
    pattern = re.compile(r'(P[O0]/No\.)(\S+)')
    for item in data:
        match = pattern.search(item['text'])
        if match:
            return match.group(2), item['conf']  # 返回 PO/No. 後面的部分和 confidence

    # 第二步：如果沒有找到，則根據關鍵字和座標提取 PO 編號
    keyword_coords = None
    po_num = None
    po_num_conf = None

    # 找到包含 PO/No. 或 P0/No. 的項目座標
    for item in data:
        for keyword in keywords:
            if keyword in item['text']:
                keyword_coords = item['coord']
                break
        if keyword_coords:
            break

    if not keyword_coords:
        return None, None  # 如果沒找到關鍵字，返回 None

    # 取得 keyword 的右側 X 坐標
    keyword_x_max = max(point[0] for point in keyword_coords)  # 取右邊界 X 坐標
    keyword_y_min = min(point[1] for point in keyword_coords)  # 取上邊界 Y 坐標
    keyword_y_max = max(point[1] for point in keyword_coords)  # 取下邊界 Y 坐標

    # 遍歷所有項目，找到位於 keyword 右側且在同一排的項目
    for item in data:
        item_coords = item['coord']
        item_x_min = min(point[0] for point in item_coords)  # 取左邊界 X 坐標
        item_y_min = min(point[1] for point in item_coords)  # 取上邊界 Y 坐標
        item_y_max = max(point[1] for point in item_coords)  # 取下邊界 Y 坐標

        # 檢查是否在 keyword 的右側並且在同一排
        if item_x_min > keyword_x_max and abs(item_y_min - keyword_y_min) < 10 and abs(item_y_max - keyword_y_max) < 10:
            po_num = item['text']
            po_num_conf = item['conf']
            break

    return po_num, po_num_conf



def common_text_extractor_main(ori_traditional_txt, image, image_height, txt_extract, ocr_reader):
    # 關鍵字的可能性宣告
    keywords_product = ['product']
    keywords_quantity = ["數量", "quantity", "shipped"]
    keywords_price = ["unit price"]
    keywords_invoice_amount = ["invoice amount", "amount"]
    keywords_batch_num = ["batch number", "batch"]
    keywords_expiry_date = ["expiry date"]

    # 提取出所有可能關鍵字的座標
    coord_product = extract_keywords_coord_from_dict(ori_traditional_txt, keywords_product)  # 提取 '品名及規格' 的座標
    coord_quantity = extract_keywords_coord_from_dict(ori_traditional_txt, keywords_quantity)  # 提取 '數量' 的座標
    coord_price = extract_keywords_coord_from_dict(ori_traditional_txt, keywords_price)  # 提取 '單價' 的座標
    coord_invoice_amount = extract_keywords_coord_from_dict(ori_traditional_txt, keywords_invoice_amount)  # 提取 '單價' 的座標
    coord_batch_num = extract_keywords_coord_from_dict(ori_traditional_txt, keywords_batch_num)  # 提取 '型號/批號' 的座標
    coord_expiry_date = extract_keywords_coord_from_dict(ori_traditional_txt, keywords_expiry_date)  # 提取 '有效期' 的座標

    # 分別提取 product, quantity, batch number, expiry date 的 ROI
    roi_product = common_extract_roi_product(image, coord_quantity, coord_product, image_height, text_height_multiplier=6)
    roi_quantity = common_extract_roi_quantity(image, coord_quantity, coord_price, text_height_multiplier=6)
    roi_batch_num = common_extract_roi_batch_num(image, coord_batch_num, coord_invoice_amount, text_height_multiplier=6)
    roi_expiry_date = common_extract_roi_expiry_date(image, coord_expiry_date, text_height_multiplier=6)

    en_product_txt, en_product_txt_conf = extract_text_conf(txt_extract, roi_product, 0, ocr_reader)
    cht_product_txt, cht_product_txt_conf = extract_text_conf(txt_extract, roi_product, 1, ocr_reader)
    quantity_txt, quantity_txt_conf = extract_text_conf(txt_extract, roi_quantity, -1, ocr_reader)
    batch_num_txt, batch_num_txt_conf = extract_text_conf(txt_extract, roi_batch_num, 0, ocr_reader)
    expiry_date_txt, expiry_date_txt_conf = extract_text_conf(txt_extract, roi_expiry_date, 0, ocr_reader)
    po_num, po_num_conf = get_po_num(ori_traditional_txt)

    result_dictionary = {
        "name": en_product_txt,
        "name_conf": en_product_txt_conf,
        "cht_name": cht_product_txt,
        "cht_name_conf": cht_product_txt_conf,
        "qty": quantity_txt,
        "qty_conf": quantity_txt_conf,
        "batch_num": batch_num_txt,
        "batch_num_conf": batch_num_txt_conf,
        "expirydate": expiry_date_txt,
        "expirydate_conf": expiry_date_txt_conf,
        "po_num": po_num,
        "po_num_conf": po_num_conf
    }

    return result_dictionary
