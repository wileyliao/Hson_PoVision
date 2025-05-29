import logging
import cv2
import matplotlib.pyplot as plt
from paddleocr import PaddleOCR, draw_ocr
import json

def read_config():
    with open("Test_config.json", "r", encoding="utf-8") as f:
        raw_text = f.read()
    raw_text = raw_text.replace("\\", "/")
    return json.loads(raw_text)

config = read_config()
image_path = config.get("image")
if not image_path:
    raise ValueError("❌ Test_config.json 中缺少 'image'")

save_path = image_path + "_with_boxes.jpg"
font_path = r"C:\Windows\Fonts\msjh.ttc"

logging.getLogger('ppocr').setLevel(logging.WARNING)
ocr = PaddleOCR(use_angle_cls=True, lang='ch')
results = ocr.ocr(image_path, cls=True)

if results and results[0]:
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    boxes = []
    for line in results[0]:
        box = line[0]
        text = line[1][0]

        y_coords = [point[1] for point in box]
        height = int(max(y_coords) - min(y_coords))
        print(f"{text} {height}")

        boxes.append(box)

    image_with_boxes = draw_ocr(image_rgb, boxes, font_path=font_path)

    plt.figure(figsize=(10, 10))
    plt.imshow(image_with_boxes)
    plt.axis('off')
    plt.show()

    image_bgr = cv2.cvtColor(image_with_boxes, cv2.COLOR_RGB2BGR)
    cv2.imwrite(save_path, image_bgr)
    print(f"✅ 已儲存：{save_path}")
else:
    print("⚠️ 沒有偵測到任何文字")
