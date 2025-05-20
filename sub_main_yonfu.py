from sub_main_yonfu_util import *
def handle_yufu(text_info, image_path):
    po_num, po_conf, po_coord = extract_po_num_yufu(text_info)
    batch, batch_conf, batch_coord = extract_batch_num_yufu(text_info, image_path)
    expiry, expiry_conf, expiry_coord = extract_expiry_yufu(text_info)

    return [{
        "po_num": (po_num, po_conf, po_coord),
        "batch_num": (batch, batch_conf, batch_coord),
        "expiry_date": (expiry, expiry_conf, expiry_coord)
    }]
