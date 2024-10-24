import re
import opencc
from Error_handler import error_handler


class TextProcessor:
    def __init__(self):
        self.converter = opencc.OpenCC('s2t')

    def convert_to_traditional(self, text):
        """轉換簡體字為繁體字"""
        if isinstance(text, list):
            # 遍歷列表並只轉換 'text' 的值
            for item in text:
                if 'text' in item:
                    item['text'] = self.converter.convert(item['text'])  # 只轉換文本部分
            return text
        elif isinstance(text, str):
            return self.converter.convert(text)
        else:
            raise TypeError("Input should be a string or a list of dictionaries with 'text' keys")

    @staticmethod
    def extract_numbers(text):
        """取文本中的數字"""
        return re.findall(r'\d+', text)

    @staticmethod
    def extract_after_no(text):
        """For process_ui_result"""
        # 使用 rsplit 從右側分割，並只分割一次
        parts = text.rsplit('no.', 1)
        if len(parts) > 1:
            return parts[1].strip()
        return text

    @staticmethod
    def preprocess_text(text):
        """For match_keywords"""
        text = text.replace('/', ' ')
        process_text = re.sub(r'\s+', '', text).lower()
        # 將 "p0" 替換為 "po" 來處理 OCR 錯誤
        process_text = process_text.replace("p0", "po")
        return process_text


@error_handler
def match_keywords(keywords, data, processor):
    matched_keywords = {}
    for keyword in keywords:
        for item in data:
            # 假設 preprocess_text 是用來處理文本的函數
            processed_keyword = processor.preprocess_text(keyword)
            processed_text = processor.preprocess_text(item['text'])
            if processed_keyword in processed_text:
                # 在返回結果中，替換文本中的 'P0' 為 'PO'
                matched_keywords[keyword] = {
                    **item,
                    'text': processed_text
                }
                break
    return matched_keywords


@error_handler
def group_same_column_by_keywords(matched_keywords, data):
    grouped_data = {}
    for keyword, info in matched_keywords.items():
        if keyword.lower() == 'pono':
            grouped_data[keyword] = [info]
            continue
        if keyword not in grouped_data:
            grouped_data[keyword] = [info]

        keyword_x_min = min(point[0] for point in info['coord'])
        keyword_x_max = max(point[0] for point in info['coord'])
        keyword_y_center = sum(point[1] for point in info['coord']) / 4  # 計算關鍵字框的中心 y 座標

        for item in data:
            if item in grouped_data[keyword]:
                continue  # 跳過已經加入的關鍵字本身
            item_x_min = min(point[0] for point in item['coord'])
            item_x_max = max(point[0] for point in item['coord'])
            item_y_center = sum(point[1] for point in item['coord']) / 4  # 計算文本框的中心 y 座標
            # 檢查是否有 x 軸範圍的重疊並且文本框在關鍵字框下方
            if keyword_x_min <= item_x_max and item_x_min <= keyword_x_max and item_y_center > keyword_y_center:
                grouped_data[keyword].append(item)
    return grouped_data


@error_handler
def batch_num_extractor(text_dict, batch_num_word):

    # 提取 'batch number' 的第一個 value 的座標
    batch_number_data = text_dict.get(batch_num_word, [])
    if not batch_number_data:
        print("找不到 'batch number' 資料")
        return text_dict  # 如果找不到資料，返回原始的 param

    # 取第一個 batch number 的座標
    first_batch_number = batch_number_data[0]
    first_coord = first_batch_number['coord']

    # 計算 b1：最左側 + 字高的一半
    left_x = first_coord[0][0]
    top_y = first_coord[0][1]
    bottom_y = first_coord[3][1]
    height = bottom_y - top_y
    b1 = left_x - (height / 2)

    # 更新批號數據
    updated_batch_number_data = []

    for value in batch_number_data:
        text = value['text']
        text_left_x = value['coord'][0][0]
        text_right_x = value['coord'][1][0]

        # 如果文字超出 b1，則進行裁剪
        if text_left_x < b1:
            text_length = len(text)
            char_width = (text_right_x - text_left_x) / text_length
            crop_position = int((b1 - text_left_x) / char_width)
            cropped_text = text[crop_position:]

            # 計算裁剪後的座標
            new_left_x = text_left_x + crop_position * char_width
            updated_coords = [
                [new_left_x, value['coord'][0][1]],
                [text_right_x, value['coord'][1][1]],
                [text_right_x, value['coord'][2][1]],
                [new_left_x, value['coord'][3][1]]
            ]

            # 更新字典的文字與座標
            updated_value = {
                'text': cropped_text,
                'coord': updated_coords,
                'conf': value['conf']
            }
        else:
            # 沒有超出範圍的保持原樣
            updated_value = value

        # 添加更新後的 value 到列表中
        updated_batch_number_data.append(updated_value)

    # 更新原始 param 結構中的 'BATCH NUMBER'
    text_dict['BATCH NUMBER'] = updated_batch_number_data

    return text_dict


def po_number_extractor(text_dict, po_keyword):
    pass


def product_info_extractor(text_dict, product_keyword):
    pass


def quantity_extractor(text_dict, quantity_keyword):
    pass


def expiry_date_extractor(text_dict, expiry_date_keyword):
    pass
