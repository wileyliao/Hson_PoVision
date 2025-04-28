import re
import opencc
from statistics import mean
from Error_handler import error_handler

@error_handler
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
def group_same_column_by_keywords(matched_keywords, text_dict):
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

        for item in text_dict:
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
def merge_same_row(data):
    updated_data = {}

    for key, entries in data.items():
        merged_entries = []
        processed = set()

        # 按照 y 座標的中心點進行排序，以便依序比較
        entries = sorted(entries, key=lambda x: (x['coord'][0][1] + x['coord'][2][1]) / 2)

        for i, entry in enumerate(entries):
            if i in processed:
                continue

            # 開始新一行的合併
            line_text = entry['text']
            line_coords = entry['coord']
            line_confidences = [entry['conf']]
            processed.add(i)

            # 計算當前文字框的中心點 y 座標和字體大小（高度）
            y1, y2 = entry['coord'][0][1], entry['coord'][2][1]
            entry_center_y = (y1 + y2) / 2
            font_size = abs(y2 - y1)
            threshold = font_size * 0.5

            # 檢查與後續項目的距離，決定是否合併
            for j in range(i + 1, len(entries)):
                if j in processed:
                    continue
                other_entry = entries[j]

                # 計算下一項目的中心點 y 座標
                oy1, oy2 = other_entry['coord'][0][1], other_entry['coord'][2][1]
                other_center_y = (oy1 + oy2) / 2

                # 判斷是否同一行：如果當前項目的中心點 y 座標 + 門檻值 大於等於 下一項目的中心點 y 座標，則合併
                if entry_center_y + threshold >= other_center_y:
                    # 合併 text 和 conf
                    line_text += ' ' + other_entry['text']
                    line_confidences.append(other_entry['conf'])
                    processed.add(j)

                    # 更新座標：擴展到包含新的座標範圍
                    line_coords = [
                        [min(line_coords[0][0], other_entry['coord'][0][0]),
                         min(line_coords[0][1], other_entry['coord'][0][1])],  # 左上
                        [max(line_coords[1][0], other_entry['coord'][1][0]),
                         min(line_coords[1][1], other_entry['coord'][1][1])],  # 右上
                        [max(line_coords[2][0], other_entry['coord'][2][0]),
                         max(line_coords[2][1], other_entry['coord'][2][1])],  # 右下
                        [min(line_coords[3][0], other_entry['coord'][3][0]),
                         max(line_coords[3][1], other_entry['coord'][3][1])]  # 左下
                    ]

            # 添加合併結果
            merged_entries.append({
                'text': line_text.strip(),
                'coord': line_coords,
                'conf': mean(line_confidences)
            })

        # 更新合併後的字典
        updated_data[key] = merged_entries

    return updated_data
