import logging
import cv2
import matplotlib.pyplot as plt
from paddleocr import PaddleOCR, draw_ocr

# 設定路徑
image_path = r"C:\pycharm\po_vision_n\po_vision_img\po_vision\CENRA\CENRA_01.jpg"
save_path = image_path+"_with_boxes.jpg"
font_path = r"C:\Windows\Fonts\msjh.ttc"

# 關掉 debug log
logging.getLogger('ppocr').setLevel(logging.WARNING)

# 初始化 OCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# 執行 OCR
results = ocr.ocr(image_path, cls=True)

# 處理結果
if results and results[0]:
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    boxes = []
    for line in results[0]:
        box = line[0]
        text = line[1][0]

        # 計算字高（max y - min y）
        y_coords = [point[1] for point in box]
        height = int(max(y_coords) - min(y_coords))
        print(f"{text} {height}")

        boxes.append(box)

    # 畫框（不顯示右側文字）
    image_with_boxes = draw_ocr(image_rgb, boxes, font_path=font_path)

    # 顯示圖
    plt.figure(figsize=(10, 10))
    plt.imshow(image_with_boxes)
    plt.axis('off')
    plt.show()

    # 儲存圖
    image_bgr = cv2.cvtColor(image_with_boxes, cv2.COLOR_RGB2BGR)
    cv2.imwrite(save_path, image_bgr)
    print(f"✅ 已儲存：{save_path}")
else:
    print("⚠️ 沒有偵測到任何文字")
