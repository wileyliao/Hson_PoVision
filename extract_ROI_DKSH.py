def calculate_text_height(coord):
    """計算文字框的高度"""
    return coord[3][1] - coord[0][1]  # 左下角的 Y 坐標 - 左上角的 Y 坐標


def dk_extract_roi_product(image, coord_quantity, coord_product, image_height, text_height_multiplier=6):
    """提取 product 的 ROI，水平範圍：'數量'的左下角到圖片最左側，垂直範圍：品名及規格的bottom往下6倍的字高"""
    # 水平範圍從圖片最左側到 '數量' 的左下角
    x_min = 0  # 圖片最左側
    x_max = int(coord_quantity[0][0])  # '數量' 的左下角 X 坐標

    # 垂直範圍從 '品名及規格' 的 bottom 往下 6 倍字高
    y_top = int(coord_product[3][1])  # '品名及規格' 的底部 Y 坐標
    text_height = calculate_text_height(coord_product)
    y_bottom = int(y_top + text_height * text_height_multiplier)  # 延伸的高度

    # 防止超出圖像邊界
    y_bottom = min(y_bottom, image_height)

    # 裁剪圖像
    roi = image[y_top:y_bottom, x_min:x_max]
    return roi


def dk_extract_roi_quantity(image, coord_quantity, coord_price, text_height_multiplier=6):
    """提取 quantity 的 ROI，水平範圍：'單價'的左下角到'數量'的最左側，垂直範圍：數量的bottom往下6倍的字高"""
    # 水平範圍從 '單價' 的左下角到 '數量' 的左下角
    x_min = int(coord_quantity[0][0])  # '數量' 的左下角 X 坐標
    x_max = int(coord_price[0][0])  # '單價' 的左下角 X 坐標

    # 垂直範圍從 '數量' 的 bottom 往下 6 倍字高
    y_top = int(coord_quantity[3][1])  # '數量' 的底部 Y 坐標
    text_height = calculate_text_height(coord_quantity)
    y_bottom = int(y_top + text_height * text_height_multiplier)  # 延伸的高度

    # 裁剪圖像
    roi = image[y_top:y_bottom, x_min:x_max]
    return roi


def dk_extract_roi_batch_num(image, coord_batch_num, text_height_multiplier=6):
    """提取 batch_num 的 ROI，水平範圍：'型號/批號'的右下角到左下角 + '型號/批號'一個字高，垂直範圍：型號/批號bottom往下6倍字高"""

    text_height = calculate_text_height(coord_batch_num)
    # 水平範圍從 '型號/批號' 的右下角到左下角 + 一個字高
    x_min = int(coord_batch_num[0][0] - text_height)  # '型號/批號' 左下角 X 坐標
    x_max = int(coord_batch_num[2][0])  # '型號/批號' 左下角加上字高

    # 垂直範圍從 '型號/批號' 的 bottom 往下 6 倍字高
    y_top = int(coord_batch_num[3][1])  # '型號/批號' 的底部 Y 坐標
    y_bottom = int(y_top + text_height * text_height_multiplier)  # 延伸的高度

    # 裁剪圖像
    roi = image[y_top:y_bottom, x_min:x_max]
    return roi


def dk_extract_roi_date(image, coord_batch_num, coord_expiry, text_height_multiplier=6):
    """提取 date 的 ROI，水平範圍：'型號/批號'的右下角到'有效期'右下角 + '有效期' 一個字高，垂直範圍：有效期bottom往下6倍字高"""
    # 水平範圍從 '型號/批號' 的右下角到 '有效期' 的右下角 + 一個字高
    x_min = int(coord_batch_num[2][0])  # '型號/批號' 右下角 X 坐標
    text_height = calculate_text_height(coord_expiry)  # 計算 '有效期' 的字高
    x_max = int(coord_expiry[2][0] + text_height)  # '有效期' 右下角加上一個字高

    # 垂直範圍從 '有效期' 的 bottom 往下 6 倍字高
    y_top = int(coord_expiry[3][1])  # '有效期' 的底部 Y 坐標
    y_bottom = int(y_top + text_height * text_height_multiplier)  # 延伸的高度

    # 裁剪圖像
    roi = image[y_top:y_bottom, x_min:x_max]
    return roi
