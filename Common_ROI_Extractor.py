def calculate_text_height(coords):
    """計算文字框的高度，支持多個座標"""
    # 使用第一組座標來計算高度
    return coords[0][3][1] - coords[0][0][1]  # 左下角的 Y 坐標 - 左上角的 Y 坐標


def get_leftmost_x_coord(coords):
    """從多組座標中提取最左邊的 X 坐標"""
    return min(point[0] for group in coords for point in group)  # 遍歷所有點，找到最小的 X 值


def get_rightmost_coord(coords):
    """從座標列表中提取最右邊的座標"""
    return max(point[0] for group in coords for point in group)  # 根據 X 坐標的最大值進行比較

def common_extract_roi_product(image, coord_quantity, coord_product, image_height, text_height_multiplier=6):
    """提取 product 的 ROI，水平範圍：'數量'的左下角到圖片最左側，垂直範圍：品名及規格的 bottom 往下 6 倍的字高"""
    text_height = calculate_text_height(coord_product)
    # 水平範圍
    x_min = 0  # 圖片最左側
    x_max = int(get_leftmost_x_coord(coord_quantity))

    # 垂直範圍
    y_top = int(coord_product[0][3][1])
    y_bottom = int(y_top + text_height * text_height_multiplier)
    y_bottom = min(y_bottom, image_height)

    # 裁剪圖像
    roi = image[y_top:y_bottom, x_min:x_max]
    return roi


def common_extract_roi_quantity(image, coord_quantity, coord_price, text_height_multiplier=6):
    """提取 quantity 的 ROI，水平範圍：'單價'的左下角到'數量'的最左側，垂直範圍：數量的bottom往下6倍的字高"""
    text_height = calculate_text_height(coord_quantity)
    # 水平範圍
    x_min = int(get_leftmost_x_coord(coord_quantity))
    x_max = int(get_leftmost_x_coord(coord_price))

    # 垂直範圍
    y_top = int(coord_quantity[0][3][1])
    y_bottom = int(y_top + text_height * text_height_multiplier)

    # 裁剪圖像
    roi = image[y_top:y_bottom, x_min:x_max]
    return roi


def common_extract_roi_batch_num(image, coord_batch_num, coord_invoice_amount, text_height_multiplier=6):
    """提取 batch_num 的 ROI，水平範圍：'型號/批號'的右下角到左下角 + '型號/批號'一個字高，垂直範圍：型號/批號bottom往下6倍字高"""
    text_height = calculate_text_height(coord_batch_num)
    # 水平範圍
    x_min = int((get_leftmost_x_coord(coord_batch_num) + get_rightmost_coord(coord_invoice_amount)))//2
    x_max = int(coord_batch_num[0][2][0])

    # 垂直範圍
    y_top = int(coord_batch_num[0][3][1])
    y_bottom = int(y_top + text_height * text_height_multiplier)

    # 裁剪圖像
    roi = image[y_top:y_bottom, x_min:x_max]
    return roi


def common_extract_roi_expiry_date(image, coord_expiry, text_height_multiplier=6):
    """提取 date 的 ROI，水平範圍：'型號/批號'的右下角到'有效期'右下角 + '有效期' 一個字高，垂直範圍：有效期bottom往下6倍字高"""
    text_height = calculate_text_height(coord_expiry)
    # 水平範圍
    x_min = int(get_leftmost_x_coord(coord_expiry))
    x_max = int(get_rightmost_coord(coord_expiry))

    # 垂直範圍
    y_top = int(coord_expiry[0][3][1])
    y_bottom = int(y_top + text_height * text_height_multiplier)

    # 裁剪圖像
    roi = image[y_top:y_bottom, x_min:x_max]
    return roi
