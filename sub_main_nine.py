from sub_main_nine_util import *

def handle_nine(text_info):
    po_num, po_num_conf, po_num_coord = extract_po_num(text_info)
    expiry_date, expiry_date_conf, expiry_date_coord = extract_expiry_date(text_info)
    batch_num, batch_num_conf, batch_num_coord = extract_batch_num(text_info, expiry_date_coord)

    return [{
        "po_num": (po_num, po_num_conf, po_num_coord),
        "expiry_date": (expiry_date, expiry_date_conf, expiry_date_coord),
        "batch_num": (batch_num, batch_num_conf, batch_num_coord)
    }]
