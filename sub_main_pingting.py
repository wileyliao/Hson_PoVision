from sub_main_pingting_util import *

def handle_pingting(text_info, structured_data):
    po_num, po_num_conf, po_num_coord = extract_po_num_pingting(structured_data)
    (batch_num, batch_conf, batch_coord), (expiry, expiry_conf, expiry_coord) = extract_batch_and_expiry_pingting(text_info)

    return {
        "po_num": (po_num, po_num_conf, po_num_coord),
        "batch_num": (batch_num, batch_conf, batch_coord),
        "expiry_date": (expiry, expiry_conf, expiry_coord)
    }
