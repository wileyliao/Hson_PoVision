from pprint import pprint
from OCR_main import po_vision_main
import os
import json
# --- 單張測試 ---
# image_path = r'po_vision_img\po_vision\大昌\dk_04.jpg'
# print("目前工作目錄：", os.getcwd())
# print("圖片存在？", os.path.exists(image_path))
#
# result = po_vision_main(image_path)
# pprint(result)


# --- 批次測試 ---
print("\n=== 批次測試開始 ===")
folder_path = r'po_vision_img\po_vision\亞洲'  # 圖片資料夾路徑
output_txt = os.path.join(folder_path, 'batch_result_output.txt')  # 存在該資料夾內

with open(output_txt, 'w', encoding='utf-8') as f:
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(folder_path, filename)
            print(f"處理中：{filename}")
            try:
                result = po_vision_main(img_path)
                json_str = json.dumps(result, ensure_ascii=False, indent=2)
                f.write(f"檔名：{filename}\n")
                f.write(f"{json_str}\n")
                f.write("-" * 40 + "\n")
            except Exception as e:
                f.write(f"檔名：{filename}\n")
                f.write(f"錯誤：{str(e)}\n")
                f.write("-" * 40 + "\n")

print(f"✅ 批次測試完成，結果已輸出至：{output_txt}")
