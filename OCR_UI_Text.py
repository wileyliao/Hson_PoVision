from Error_handler import error_handler


@error_handler
def process_ui_result(grouped_data, processor):
    saved_dict = {}
    for keyword, items in grouped_data.items():
        group_name = processor.convert_to_traditional(keyword).lower()

        if group_name == 'pono':
            item = items[0] if items else None
            if item:
                text = processor.extract_after_no(item['text'])
                if text.strip():
                    saved_dict['po_num'] = text
                    saved_dict['po_num_conf'] = str(item['conf'])
                else:
                    saved_dict['po_num'] = ''
                    saved_dict['po_num_conf'] = ''
            else:
                saved_dict['po_num'] = ''
                saved_dict['po_num_conf'] = ''

        elif group_name == 'product':
            # 提取兩個產品名，第一個是英文，第二個是中文
            if len(items) > 1:
                saved_dict['name'] = items[1]['text']
                saved_dict['name_conf'] = str(items[1]['conf'])
            else:
                saved_dict['name'] = ''
                saved_dict['name_conf'] = ''

            if len(items) > 2:
                saved_dict['cht_name'] = items[2]['text']
                saved_dict['cht_name_conf'] = str(items[2]['conf'])
            else:
                saved_dict['cht_name'] = ''
                saved_dict['cht_name_conf'] = ''

        elif group_name == 'quantity':
            # 提取數字
            if items:
                for item in items:
                    text = ''.join(processor.extract_numbers(item['text']))
                    if text.strip():
                        saved_dict['qty'] = text
                        saved_dict['qty_conf'] = str(item['conf'])
                        break
                else:
                    saved_dict['qty'] = ''
                    saved_dict['qty_conf'] = ''
            else:
                saved_dict['qty'] = ''
                saved_dict['qty_conf'] = ''

        elif group_name == 'batch number':
            # 提取批號
            if items:
                item = items[1] if len(items) > 1 else items[0]
                saved_dict['batch_num'] = item['text']
                saved_dict['batch_num_conf'] = str(item['conf'])
            else:
                saved_dict['batch_num'] = ''
                saved_dict['batch_num_conf'] = ''

        elif group_name == 'expirydate':
            # 提取有效日期
            if items:
                for item in items:
                    text = ''.join(processor.extract_numbers(item['text']))
                    if text.strip():
                        saved_dict['expirydate'] = text
                        saved_dict['expirydate_conf'] = str(item['conf'])
                        break
                else:
                    saved_dict['expirydate'] = ''
                    saved_dict['expirydate_conf'] = ''
            else:
                saved_dict['expirydate'] = ''
                saved_dict['expirydate_conf'] = ''

    return saved_dict
