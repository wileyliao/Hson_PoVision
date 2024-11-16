from Error_handler import error_handler


@error_handler
def batch_num_extractor(text_dict, batch_num_word):

    # 提取 'batch number' 的第一個 value 的座標
    batch_num_data = text_dict.get(batch_num_word, [])
    batch_num_keyword_coord = batch_num_data[0]['coord']

    # 計算左邊界：最左側 + 字高的一半 (計算 b1)
    left_x = batch_num_keyword_coord[0][0]
    top_y = batch_num_keyword_coord[0][1]
    bottom_y = batch_num_keyword_coord[3][1]
    height = bottom_y - top_y
    left_edge = left_x - (height / 2)

    # 取批號文字與座標
    batch_num_text = batch_num_data[1]['text']
    batch_num_text_left_x = batch_num_data[1]['coord'][0][0]
    batch_num_text_right_x = batch_num_data[1]['coord'][1][0]

    # 如果文字超出left_edge，則進行裁剪
    if batch_num_text_left_x < left_edge:
        text_length = len(batch_num_text)
        char_width = (batch_num_text_right_x - batch_num_text_left_x) / text_length
        crop_position = int((left_edge - batch_num_text_left_x) / char_width)
        cropped_text = batch_num_text[crop_position:].replace(" ", "")
    else:
        cropped_text = batch_num_text

    return cropped_text, batch_num_data[1]['conf'], batch_num_data[1]['coord']


@error_handler
def po_number_extractor_en(text_dict, po_keyword, processor):
    # 提取 'po number' 的第一個 value 的座標
    po_num_text = text_dict.get(po_keyword, [])[0]['text']
    processed_text = processor.extract_after_no(po_num_text)

    return processed_text, text_dict.get(po_keyword, [])[0]['conf'], text_dict.get(po_keyword, [])[0]['coord']


@error_handler
def po_number_extractor_cht(text_dict, po_keyword):
    # 找到 po_keyword 的座標資訊
    po_box = None
    for item in text_dict:
        if item['text'] == po_keyword:
            po_box = item
            break

    if not po_box:
        print("PO keyword not found.")
        return []

    # 計算 po_keyword 的最右側 x 座標 (a) 和字高 (b)
    a = max(po_box['coord'][1][0], po_box['coord'][2][0])  # 取得最右側 x 座標
    b = abs(po_box['coord'][2][1] - po_box['coord'][0][1])  # 計算字高
    y_threshold = b * 0.5  # 設定 y 座標閥值
    po_center_y = (po_box['coord'][0][1] + po_box['coord'][2][1]) / 2

    # 遍歷字典中的文字框，尋找符合條件的右邊文字框
    right_boxes = []
    for item in text_dict:
        # 跳過 po_keyword 本身
        if item['text'] == po_keyword:
            continue

        # 使用 item 的 x 軸中心點進行比較
        item_center_x = (item['coord'][0][0] + item['coord'][1][0]) / 2
        if item_center_x <= a:
            continue  # 若文字框中心點不在 po_keyword 右側，跳過

        # 檢查 y 座標閥值範圍
        item_center_y = (item['coord'][0][1] + item['coord'][2][1]) / 2
        if abs(item_center_y - po_center_y) <= y_threshold:
            right_boxes.append(item)  # 加入符合條件的右側文字框

    return right_boxes[0]['text'], right_boxes[0]['conf'], right_boxes[0]['coord']


@error_handler
def product_info_extractor_en_first(text_dict, product_keyword):
    # 提取關鍵字對應的值
    product_data = text_dict.get(product_keyword, [])

    if len(product_data) < 3:
        return [], []

    # 直接提取文字和置信度到列表中
    text_list = [product_data[1]['text'], product_data[2]['text']]
    conf_list = [product_data[1]['conf'], product_data[2]['conf']]
    coord_list = [product_data[1]['coord'], product_data[2]['coord']]

    return text_list, conf_list, coord_list


@error_handler
def product_info_extractor_cht_first(text_dict, product_keyword):
    # 提取關鍵字對應的值
    product_data = text_dict.get(product_keyword, [])

    if len(product_data) < 3:
        return [], []

    # 直接提取文字和置信度到列表中
    text_list = [product_data[2]['text'], product_data[1]['text']]
    conf_list = [product_data[2]['conf'], product_data[1]['conf']]
    coord_list = [product_data[2]['coord'], product_data[1]['coord']]

    return text_list, conf_list, coord_list


@error_handler
def quantity_extractor(text_dict, quantity_keyword):
    quantity_text = text_dict.get(quantity_keyword, [])[-1]['text']
    quantity_text_conf = text_dict.get(quantity_keyword, [])[-1]['conf']
    quantity_text_coord = text_dict.get(quantity_keyword, [])[-1]['coord']

    return quantity_text, quantity_text_conf, quantity_text_coord


@error_handler
def expiry_date_extractor_en(text_dict, expiry_date_keyword):
    expiry_date_text = text_dict.get(expiry_date_keyword, [])[1]['text']
    expiry_date_text_conf = text_dict.get(expiry_date_keyword, [])[1]['conf']
    expiry_date_text_coord = text_dict.get(expiry_date_keyword, [])[1]['coord']

    return expiry_date_text, expiry_date_text_conf, expiry_date_text_coord


@error_handler
def expiry_date_extractor_cht(text_dict, expiry_date_keyword):
    expiry_date_text = text_dict.get(expiry_date_keyword, [])[-1]['text']
    expiry_date_text_conf = text_dict.get(expiry_date_keyword, [])[-1]['conf']
    expiry_date_text_coord = text_dict.get(expiry_date_keyword, [])[-1]['coord']

    return expiry_date_text, expiry_date_text_conf, expiry_date_text_coord
