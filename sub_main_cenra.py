from sub_main_cenra_util import *

def handle_cenra(structured_data, text_info, degree="0"):
    po_num, po_num_conf, po_num_coord = extract_po_num(text_info)
    expiry_items = extract_expiry_dates(structured_data)
    batch_items = extract_batch_nums(structured_data)

    # 依 Y 座標排序（由上往下）
    expiry_items.sort(key=lambda item: item[2][0][1])  # expiry_coord 的 y 值
    batch_items.sort(key=lambda item: item[2][0][1])   # batch_coord 的 y 值

    records = []
    for i in range(min(len(expiry_items), len(batch_items))):
        expiry_text, expiry_conf, expiry_coord = expiry_items[i]
        batch_text, batch_conf, batch_coord = batch_items[i]
        records.append({
            "po_num": (po_num, po_num_conf, po_num_coord),
            "expiry_date": (expiry_text, expiry_conf, expiry_coord),
            "batch_num": (batch_text, batch_conf, batch_coord)
        })

    # fallback：若沒成功配對，也要回傳一筆空資料
    if not records:
        records = [{
            "po_num": (po_num, po_num_conf, po_num_coord),
            "expiry_date": ("", 0, [[0, 0]] * 4),
            "batch_num": ("", 0, [[0, 0]] * 4)
        }]

    return records, "True" if records else "False"
