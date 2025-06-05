from sub_main_cenra_util import extract_po_num_cenra, extract_batch_num_cenra, extract_expiry_date_cenra

def handle_cenra(text_info):
    po_num, po_num_conf, po_num_coord = extract_po_num_cenra(text_info)
    batch_num, batch_num_conf, batch_num_coord = extract_batch_num_cenra(text_info)
    expiry, expiry_conf, expiry_coord = extract_expiry_date_cenra(text_info)

    return {
        "po_num": (po_num, po_num_conf, po_num_coord),
        "batch_num": (batch_num, batch_num_conf, batch_num_coord),
        "expiry_date": (expiry, expiry_conf, expiry_coord)
    }
