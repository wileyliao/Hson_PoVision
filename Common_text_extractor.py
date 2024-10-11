from Common_ROI_Extractor import *
import cv2


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


def common_text_extractor_main(ori_traditional_txt, image, image_height, txt_extract, ocr_reader):
    # 關鍵字的可能性宣告
    keywords_product = ['product code and description']
    keywords_quantity = ["數量", "quantity", "shipped"]
    keywords_price = ["unit price"]
    keywords_invoice_amount = ["invoice amount"]
    keywords_batch_num = ["batch number"]
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

    # cv2.imshow('product', roi_product)
    # cv2.imshow('quantity', roi_quantity)
    # cv2.imshow('batch_num', roi_batch_num)
    # cv2.imshow('date', roi_expiry_date)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    en_product_txt, en_product_txt_conf = extract_text_conf(txt_extract, roi_product, 0, ocr_reader)
    cht_product_txt, cht_product_txt_conf = extract_text_conf(txt_extract, roi_product, 1, ocr_reader)
    quantity_txt, quantity_txt_conf = extract_text_conf(txt_extract, roi_quantity, -1, ocr_reader)
    batch_num_txt, batch_num_txt_conf = extract_text_conf(txt_extract, roi_batch_num, 0, ocr_reader)
    expiry_date_txt, expiry_date_txt_conf = extract_text_conf(txt_extract, roi_expiry_date, 0, ocr_reader)

    print(f'coord_product {coord_product}')
    print(f'coord_quantity {coord_quantity}')
    print(f'coord_price {coord_price}')
    print(f'coord_invoice_amount {coord_invoice_amount}')
    print(f'coord_batch_num {coord_batch_num}')
    print(f'coord_expiry {coord_expiry_date}')

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
        # "po_num": po_number,
        # "po_num_conf": po_number_conf
    }

    return result_dictionary
