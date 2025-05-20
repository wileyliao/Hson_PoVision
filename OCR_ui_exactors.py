import re

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


def batch_num_extractor_dk(text_dict, batch_num_word):
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
    batch_num_text = batch_num_data[-1]['text']
    batch_num_text_left_x = batch_num_data[-1]['coord'][0][0]
    batch_num_text_right_x = batch_num_data[-1]['coord'][1][0]

    # 如果文字超出left_edge，則進行裁剪
    if batch_num_text_left_x < left_edge:
        text_length = len(batch_num_text)
        char_width = (batch_num_text_right_x - batch_num_text_left_x) / text_length
        crop_position = int((left_edge - batch_num_text_left_x) / char_width)
        cropped_text = batch_num_text[crop_position:].replace(" ", "")
    else:
        cropped_text = batch_num_text

    return cropped_text, batch_num_data[-1]['conf'], batch_num_data[-1]['coord']


def po_number_extractor_en(text_dict, po_keyword, processor):
    po_num_text = text_dict.get(po_keyword, [])[0]['text']
    processed_text = processor.extract_after_no(po_num_text)

    return processed_text, text_dict.get(po_keyword, [])[0]['conf'], text_dict.get(po_keyword, [])[0]['coord']



def po_number_extractor_cht(text_dict, po_keyword):
    # 找到 po_keyword 的座標資訊
    po_box = None
    for item in text_dict:
        if po_keyword in item['text']:
            po_box = item
            if len(po_box['text']) > 10:
                return po_box['text'][-16:], po_box['conf'], po_box['coord']
            break

    if not po_box:
        print("PO keyword not found.")
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]

    # 計算 po_keyword 的最右側 x 座標 (a) 和字高 (b)
    a = max(po_box['coord'][1][0], po_box['coord'][2][0])
    b = abs(po_box['coord'][2][1] - po_box['coord'][0][1])
    y_threshold = b * 0.5
    po_center_y = (po_box['coord'][0][1] + po_box['coord'][2][1]) / 2

    # 遍歷文字框，尋找右側符合條件的框
    right_boxes = []
    for item in text_dict:
        if item['text'] == po_keyword:
            continue

        item_center_x = (item['coord'][0][0] + item['coord'][1][0]) / 2
        if item_center_x <= a:
            continue

        item_center_y = (item['coord'][0][1] + item['coord'][2][1]) / 2
        if abs(item_center_y - po_center_y) <= y_threshold and len(item['text']) >= 16:
            item['text'] = item['text'][-16:]
            right_boxes.append(item)
    print("right box: ", right_boxes)

    if not right_boxes:
        print("No valid right box found.")
        return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]

    return right_boxes[0]['text'], right_boxes[0]['conf'], right_boxes[0]['coord']



def product_info_extractor_en_first(text_dict, product_keyword):
    product_data = text_dict.get(product_keyword, [])

    if len(product_data) < 3:
        return [], []

    # 直接提取文字和置信度到列表中
    text_list = [product_data[1]['text'], product_data[2]['text']]
    conf_list = [product_data[1]['conf'], product_data[2]['conf']]
    coord_list = [product_data[1]['coord'], product_data[2]['coord']]

    return text_list, conf_list, coord_list


def product_info_extractor_cht_first(text_dict, product_keyword):
    product_data = text_dict.get(product_keyword, [])

    if len(product_data) < 3:
        return [], []

    # 直接提取文字和置信度到列表中
    text_list = [product_data[2]['text'], product_data[1]['text']]
    conf_list = [product_data[2]['conf'], product_data[1]['conf']]
    coord_list = [product_data[2]['coord'], product_data[1]['coord']]

    return text_list, conf_list, coord_list



def quantity_extractor(text_dict, quantity_keyword):
    quantity_text = text_dict.get(quantity_keyword, [])[-1]['text']
    quantity_text_conf = text_dict.get(quantity_keyword, [])[-1]['conf']
    quantity_text_coord = text_dict.get(quantity_keyword, [])[-1]['coord']

    return quantity_text, quantity_text_conf, quantity_text_coord


def expiry_date_extractor_en(text_dict, expiry_date_keyword):
    expiry_date_text = text_dict.get(expiry_date_keyword, [])[1]['text']
    expiry_date_text_conf = text_dict.get(expiry_date_keyword, [])[1]['conf']
    expiry_date_text_coord = text_dict.get(expiry_date_keyword, [])[1]['coord']

    return expiry_date_text, expiry_date_text_conf, expiry_date_text_coord



def expiry_date_extractor_cht(text_dict, expiry_date_keyword):
    expiry_date_text = text_dict.get(expiry_date_keyword, [])[-1]['text']
    expiry_date_text_conf = text_dict.get(expiry_date_keyword, [])[-1]['conf']
    expiry_date_text_coord = text_dict.get(expiry_date_keyword, [])[-1]['coord']

    return expiry_date_text, expiry_date_text_conf, expiry_date_text_coord


def expiry_date_extractor_nine(text_dict):
    date_pattern = re.compile(r"^\d{4}/\d{2}/\d{2}$")
    date_entry = next((entry for entry in text_dict if date_pattern.match(entry['text'])), None)

    return date_entry['text'], date_entry['conf'], date_entry['coord']

def batch_num_extractor_nine(text_dict,expiry_date_coord):
    # 計算 po_keyword 的最右側 x 座標 (a) 和字高 (b)
    most_right = max(expiry_date_coord[1][0], expiry_date_coord[2][0])  # 取得最右側 x 座標
    text_height = abs(expiry_date_coord[2][1] - expiry_date_coord[0][1])  # 計算字高
    y_threshold = text_height * 0.5  # 設定 y 座標閥值
    center_y = (expiry_date_coord[0][1] + expiry_date_coord[2][1]) / 2

    # 記錄當前最近的 box
    closest_box = None
    min_x_distance = float('inf')  # 記錄目前最近的 x 距離

    for item in text_dict:
        # 計算 X, Y 軸中心點
        item_center_x = (item['coord'][0][0] + item['coord'][1][0]) / 2
        item_center_y = (item['coord'][0][1] + item['coord'][2][1]) / 2

        # X 軸條件：必須在 `most_right` 右邊
        if item_center_x <= most_right:
            continue

            # Y 軸條件：中心 Y 值必須在允許範圍內，並且 X 軸距離最近
        x_distance = item_center_x - most_right  # 計算與 `most_right` 的距離

        if abs(item_center_y - center_y) <= y_threshold and x_distance < min_x_distance:
            closest_box = item
            min_x_distance = x_distance  # 更新最小 X 距離

    # 如果有找到符合條件的最近框，就只保留這個
    right_boxes = [closest_box] if closest_box else []

    return right_boxes[-1]['text'], right_boxes[-1]['conf'], right_boxes[-1]['coord']





