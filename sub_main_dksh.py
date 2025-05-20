from sub_main_dksh_util import *

def handle_dksh(text_info, structured_data):
    po_num, po_num_conf, po_num_coord = extract_po_num(text_info)
    expiry_date, expiry_date_conf, expiry_date_coord = extract_expiry_date(structured_data)
    batch_num, batch_num_conf, batch_num_coord = extract_batch_num(structured_data)

    return [{
        "po_num": (po_num, po_num_conf, po_num_coord),
        "expiry_date": (expiry_date, expiry_date_conf, expiry_date_coord),
        "batch_num": (batch_num, batch_num_conf, batch_num_coord)
    }]
