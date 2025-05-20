from sub_main_dq_util import *

def handle_dq(text_blocks, _=None):
    po_num, po_num_conf, po_num_coord = extract_po_num_dq(text_blocks)
    batch_num, batch_num_conf, batch_num_coord = extract_batch_num_dq(text_blocks)
    expiry_date, expiry_date_conf, expiry_date_coord = extract_expiry_date_dq(text_blocks)

    return [{
        "po_num": (po_num, po_num_conf, po_num_coord),
        "batch_num": (batch_num, batch_num_conf, batch_num_coord),
        "expiry_date": (expiry_date, expiry_date_conf, expiry_date_coord)
    }]
