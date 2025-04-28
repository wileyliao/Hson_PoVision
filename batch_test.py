import requests
import json
import base64
import os
import tkinter as tk
from tkinter import filedialog

# 圖片轉 base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        b64_string = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_string}"

# 選取資料夾
def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="選擇圖片資料夾")
    return folder_selected

# 發送圖片給 API 並回傳結果
def process_image(image_path, url):
    base64_string = encode_image_to_base64(image_path)
    payload = {
        "Data": [
            {
                "base64": base64_string,
                "GUID": "0030679"
            }
        ]
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        response_data = response.json()
        print(f"✔ {os.path.basename(image_path)} 回傳資料：")
        print(json.dumps(response_data, indent=4, ensure_ascii=False))
        return response_data
    else:
        print(f"✘ {os.path.basename(image_path)} API 請求失敗，狀態碼：", response.status_code)
        return {"error": f"API 請求失敗，狀態碼：{response.status_code}"}

# 從回傳中萃取三個欄位
def extract_fields(data):
    try:
        fields = data.get("Data", [{}])[0]
        return {
            "batch_num": fields.get("batch_num"),
            "expirydate": fields.get("expirydate"),
            "po_num": fields.get("po_num")
        }
    except Exception as e:
        return {"error": str(e)}

# 主流程
def main():
    url = "https://www.kutech.tw:3000/po_vision"  # 替換為您的 API URL
    folder_path = select_folder()
    if not folder_path:
        print("未選取任何資料夾。")
        return

    image_extensions = (".jpg", ".jpeg", ".png")
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]

    if not image_files:
        print("選取的資料夾中沒有圖片檔案。")
        return

    print(f"共找到 {len(image_files)} 張圖片，開始處理...\n")

    results = {}
    for img_file in image_files:
        image_path = os.path.join(folder_path, img_file)
        response_data = process_image(image_path, url)
        results[img_file] = extract_fields(response_data)

    # 儲存結果成 json 格式的 .txt 檔
    result_file = os.path.join(folder_path, "OCR_results.txt")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"\n所有結果已儲存至：{result_file}")

if __name__ == "__main__":
    main()
