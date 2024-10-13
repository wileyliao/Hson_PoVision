from paddleocr import PaddleOCR
from OCR_txt_utils import *
from OCR_img_utils import *
from DKSH_text_extractor import dksh_text_extractor_main
from Common_text_extractor import common_text_extractor_main

from Company_Checker import company_checker_main

import logging
import cv2
from OCR_UI_Text import process_ui_result


def calculate_average_slope_and_bottom(data, keywords):
    slopes = []
    bottom_points = []

    for keyword in keywords:
        keyword_coords = None

        # 找到每個關鍵字的座標
        for item in data:
            if keyword.lower() in item['text'].lower():
                keyword_coords = item['coord']
                break

        if keyword_coords is None:
            print(f"未找到關鍵字: {keyword}")
            continue

        # 根據左上角和右上角計算斜率
        x1, y1 = keyword_coords[0]  # 左上角
        x2, y2 = keyword_coords[1]  # 右上角
        if x2 != x1:
            slope = (y2 - y1) / (x2 - x1)  # 斜率計算
            slopes.append(slope)
        else:
            slopes.append(0)  # 如果 x 相等，斜率為 0

        # 找到該關鍵字的右下角或左下角的 Y 坐標
        bottom_left = keyword_coords[0]  # 左下角
        bottom_right = keyword_coords[1]  # 右下角
        bottom_points.append((bottom_left[1] + bottom_right[1]) / 2)  # 計算下方平均點的 Y 坐標

    if not slopes or not bottom_points:
        return None, None  # 如果沒有斜率或下方點，返回 None

    # 計算斜率和最下方點的平均值
    average_slope = np.mean(slopes)
    average_bottom_y = np.mean(bottom_points)

    return average_slope, average_bottom_y


def crop_below_based_on_slope(image, average_slope, average_bottom_y):
    img_height, img_width = image.shape[:2]

    # 定義裁剪區域的四個頂點
    left_x = 0
    right_x = img_width

    # 根據斜率計算左下角和右下角的 Y 坐標
    left_y = int(average_bottom_y)  # 左邊起始點
    right_y = int(average_bottom_y + average_slope * (right_x - left_x))  # 根據斜率計算右邊

    # 如果斜率過大，保證範圍在圖像內
    if left_y > img_height or right_y > img_height:
        left_y = min(left_y, img_height)
        right_y = min(right_y, img_height)

    # 定義裁剪區域
    crop_coords = np.array([
        [left_x, left_y],  # 左上角
        [right_x, right_y],  # 右上角
        [right_x, img_height],  # 右下角
        [left_x, img_height]  # 左下角
    ], dtype=np.int32)

    # 根據四個頂點裁剪影像
    mask = np.zeros_like(image)  # 創建與圖像大小相同的空白掩膜
    cv2.fillPoly(mask, [crop_coords], (255, 255, 255))  # 填充多邊形區域

    # 將圖像與掩膜結合，得到裁剪後的部分
    cropped_image = cv2.bitwise_and(image, mask)

    # 根據掩膜的邊界提取裁剪區域
    x_min, y_min = np.min(crop_coords, axis=0)
    x_max, y_max = np.max(crop_coords, axis=0)

    # 最終裁剪
    final_cropped_image = cropped_image[y_min:y_max, x_min:x_max]

    return final_cropped_image


def txt_extract(img, reader):
    results = reader.ocr(img, cls=True)
    extracted_data = []
    for bbox, (text, score) in results[0]:
        extracted_data.append({
            "text": text,
            "coord": bbox,
            "conf": score
        })
    return extracted_data


def po_vision_main(image_path, keywords):
    def sort_by_coordinates(data):
        sorted_data = sorted(
            data,
            key=lambda item: (
                min(coord[1] for coord in item['coord']),  # 先按 Y 坐標排序
                min(coord[0] for coord in item['coord'])  # 再按 X 坐標排序
            )
        )
        return sorted_data

    def find_two_leftmost_bottom(data):
        # 先按 X 坐標排序，再按 Y 坐標（越大越靠下）
        sorted_data = sorted(
            data,
            key=lambda item: (
                min(coord[0] for coord in item['coord']),  # 先按 X 坐標排序
                -max(coord[1] for coord in item['coord'])  # 再按 Y 坐標排序，Y 越大越靠下
            )
        )
        # 返回最左下的兩個字
        return sorted_data[:2]  # 返回前兩個最左且最下的文字框

    # Initial OCR reader and text processor
    ocr_reader = PaddleOCR(use_angle_cls=True, lang='ch')
    processor = TextProcessor()

    # image processing
    image = cv2.imread(image_path)
    image_height, image_width, _ = image.shape

    # Check Company Info
    company = company_checker_main(image, ocr_reader, processor)
    print(f'公司名稱：{company}')

    if company == "大昌":
        image_dk = cut_roi_by_ratio(image, 0.15, 0.4)
        image_dk_height, image_dk_width, _ = image_dk.shape
        image_dk_txt_origin = txt_extract(image_dk, ocr_reader)
        image_dk_txt_traditional = processor.convert_to_traditional(image_dk_txt_origin)
        result_dict = dksh_text_extractor_main(image_dk_txt_traditional, image_dk, image_dk_height, txt_extract, ocr_reader)
        logging.info(f'Result :{result_dict}')
        return result_dict
    else:
        image_common = cut_roi_by_ratio(image, 0.2, 0.45)
        image_common_height, image_common_width, _ = image_common.shape
        image_common_txt_origin = txt_extract(image_common, ocr_reader)
        image_common_txt_traditional = processor.convert_to_traditional(image_common_txt_origin)
        print(image_common_txt_traditional)
        logging.info(f'Original text: {image_common_txt_traditional}')

        average_slope, average_bottom_y = calculate_average_slope_and_bottom(image_common_txt_traditional,
                                                                             ["product", "price", "amount", "batch",
                                                                              "expiry"])
        if average_slope is not None and average_bottom_y is not None:
            cropped_image = crop_below_based_on_slope(image_common, average_slope, average_bottom_y)
            cv2.imshow('cut', cropped_image)
            cv2.waitKey(0)
            cv2.destroyWindow()

        # result_dict = common_text_extractor_main(image_common_txt_traditional, image_common, image_common_height, txt_extract, ocr_reader)
        return

    # # Get the company of the PO
    # pharma_company = find_company_in_top_n(ori_traditional_txt, top_n=5, pharma_company_set=pharma_company_set)
    # logging.info(f'Company: {pharma_company}')
    #
    # # Determine which Algo will use
    # if pharma_company == '大昌':
    #     result_dict = dksh_text_extractor_main(ori_traditional_txt, image, image_height, txt_extract, ocr_reader)
    #     logging.info(f'Result :{result_dict}')
    #     return result_dict
    #
    # else:
    #     result_dict = common_text_extractor_main(ori_traditional_txt, image, image_height, txt_extract, ocr_reader)
    #     logging.info(f'Result :{result_dict}')
    #     return result_dict


if __name__ == '__main__':
    company_set = {'大昌', '裕利', '和安', '中外'}

    keywords = [
        "PONO",
        "PRODUCT",
        "QUANTITY",
        "BATCH NUMBER",
        "EXPIRY DATE"
    ]

    print(po_vision_main('./test/08.jpg', keywords))


