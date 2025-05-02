import re

import re

def extract_po_num_dq(text_blocks):
    for block in text_blocks:
        text = block['text']
        if "原客戶訂" in text:
            # 嘗試用所有常見冒號符號切開
            for delim in [':', '：', '﹕', '꞉']:
                if delim in text:
                    parts = text.split(delim)
                    if len(parts) > 1:
                        po = parts[1].strip()
                        # 防止有其他雜訊，保守取字母數字.- 組成的部分
                        match = re.match(r'([A-Z0-9.\-]+)', po)
                        if match:
                            return match.group(1), 0.99, block['coord']
    return "", 0, [[0, 0]] * 4





def extract_batch_num_dq(text_blocks):
    for block in text_blocks:
        text = block['text']
        if "批號" in text:
            match = re.search(r'批號[:：]?\s*([A-Z0-9\-]+)', text)
            if match:
                return match.group(1), 0.99, block['coord']
    return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]


def extract_expiry_date_dq(text_blocks):
    """
    只從包含 '效期' 關鍵字的文字區塊中抓 YYYY/MM/DD。
    """
    for block in text_blocks:
        text = block['text']
        if "效期" in text or "有效期限" in text:
            match = re.search(r'(\d{4}/\d{2}/\d{2})', text)
            if match:
                return match.group(1), 0.99, block['coord']
    return "", 0, [[0, 0], [0, 0], [0, 0], [0, 0]]

