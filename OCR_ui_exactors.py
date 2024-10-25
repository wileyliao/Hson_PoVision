from Error_handler import error_handler


@error_handler
def batch_num_extractor(text_dict, batch_num_word, processor):

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

    return cropped_text, batch_num_data[1]['conf']


@error_handler
def po_number_extractor_en(text_dict, po_keyword, processor):
    # 提取 'po number' 的第一個 value 的座標
    po_num_text = text_dict.get(po_keyword, [])[0]['text']
    processed_text = processor.extract_after_no(po_num_text)

    return processed_text, text_dict.get(po_keyword, [])[0]['conf']


@error_handler
def product_info_extractor(text_dict, product_keyword):
    # 提取關鍵字對應的值
    product_data = text_dict.get(product_keyword, [])

    # 直接提取文字和置信度到列表中
    text_list = [product_data[-1]['text'], product_data[-2]['text']]
    conf_list = [product_data[-1]['conf'], product_data[-2]['conf']]

    return text_list, conf_list


@error_handler
def quantity_extractor(text_dict, quantity_keyword):
    quantity_text = text_dict.get(quantity_keyword, [])[-1]['text']
    quantity_text_conf = text_dict.get(quantity_keyword, [])[-1]['conf']

    return quantity_text, quantity_text_conf


@error_handler
def expiry_date_extractor(text_dict, expiry_date_keyword):
    expiry_date_text = text_dict.get(expiry_date_keyword, [])[1]['text']
    expiry_date_text_conf = text_dict.get(expiry_date_keyword, [])[1]['conf']

    return expiry_date_text, expiry_date_text_conf

