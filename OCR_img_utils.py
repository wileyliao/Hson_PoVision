import cv2
import base64
import numpy as np
from Error_handler import error_handler


@error_handler
def base64_decoder(image_64):
    decode = base64.b64decode(image_64)
    image_array = np.frombuffer(decode, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


@error_handler
def cut_roi_from_image(image, y_top_ratio, y_bottom_ratio):
    # 獲取圖像的高度和寬度
    height, width, _ = image.shape

    # 使用比例計算出新的 y 座標
    y1 = int(y_top_ratio * height)
    y2 = int(y_bottom_ratio * height)

    # x 方向覆蓋整個圖像的寬度
    roi_image = image[y1:y2, 0:width]

    return roi_image
