import re
import opencc
from Error_handler import error_handler


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
def match_keywords(keyword_mapping, text_dict, processor):
    matched_keywords_dict = {}
    for main_keyword, info in keyword_mapping.items():
        # 使用新字典結構中的 "keywords" 列表
        for keyword in info["keywords"]:
            for item in text_dict:
                # 假設 preprocess_text 是用來處理文本的函數
                processed_keyword = processor.preprocess_text(keyword)
                processed_text = processor.preprocess_text(item['text'])
                if processed_keyword in processed_text:
                    # 在返回結果中，替換文本中的 'P0' 為 'PO'
                    matched_keywords_dict[main_keyword] = {
                        **item,
                        'text': processed_text
                    }
                    break
            # 如果已找到匹配的主關鍵字，跳出內層迴圈
            if main_keyword in matched_keywords_dict:
                break
    return matched_keywords_dict


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

