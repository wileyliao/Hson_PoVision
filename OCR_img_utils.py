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
def cut_roi_from_image(image, coords):
    (x1, y1), (x2, y2) = coords
    top_left_x = min(x1, x2)
    top_left_y = min(y1, y2)
    bottom_right_x = max(x1, x2)
    bottom_right_y = max(y1, y2)
    roi_image = image[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
    return roi_image
