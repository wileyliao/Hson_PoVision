# sub_main_psh.py
from sub_main_psh_util import *

def handle_psh(text_info, structured_data):
    po_num, po_num_conf, po_num_coord = extract_po_num_psh(text_info)
    batch_num, batch_conf, batch_coord = extract_batch_num_psh(text_info)
    expiry_date, expiry_conf, expiry_coord = extract_expiry_date_psh(text_info)

    return [{
        "po_num": (po_num, po_num_conf, po_num_coord),
        "batch_num": (batch_num, batch_conf, batch_coord),
        "expiry_date": (expiry_date, expiry_conf, expiry_coord)
    }]
