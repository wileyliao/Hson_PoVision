import cv2
import base64
import numpy as np


def base64_decoder(image_64):
    decode = base64.b64decode(image_64)
    image_array = np.frombuffer(decode, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    # cv2.imshow("image", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return image


def image_to_base64(image_path):
    # 讀取圖片並轉換為 Base64 字串
    with open(image_path, "rb") as image_file:
        # 將圖片內容編碼為 Base64
        base64_string = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_string


def cut_roi_by_ratio(image, y_top_ratio, y_bottom_ratio):
    # 獲取圖像的高度和寬度
    height, width, _ = image.shape

    # 使用比例計算出新的 y 座標
    y1 = int(y_top_ratio * height)
    y2 = int(y_bottom_ratio * height)

    # x 方向覆蓋整個圖像的寬度
    roi_image = image[y1:y2, 0:width]

    return roi_image


if __name__ == "__main__":
    image_p = 'output_image.png'
    bs64_tring = image_to_base64(image_p)
    print(bs64_tring)
