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

# 從回傳中萃取多筆資料欄位
def extract_fields(data):
    try:
        items = data.get("Data", [])
        time_taken = data.get("TimeTaken", "N/A")
        results = []

        for item in items:
            results.append({
                "po_num": item.get("po_num", ""),
                "batch_num": item.get("batch_num", ""),
                "expirydate": item.get("expirydate", ""),
                "TimeTaken": time_taken
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]

# 主流程
def main():
    url = "https://www.kutech.tw:3000/Po_Vision"
    selected_folder = select_folder()
    if not selected_folder:
        print("未選取任何資料夾。")
        return

    image_extensions = (".jpg", ".jpeg", ".png")
    results = {}
    error_files = []

    def process_folder(folder_path, folder_label):
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
        if not image_files:
            return False

        print(f"[{folder_label}] 共找到 {len(image_files)} 張圖片，開始處理...\n")

        for img_file in image_files:
            image_path = os.path.join(folder_path, img_file)
            response_data = process_image(image_path, url)
            extracted_items = extract_fields(response_data)
            results[f"{folder_label}/{img_file}"] = extracted_items

            if not extracted_items:
                error_files.append(f"{folder_label}/{img_file}")
                continue

            for item in extracted_items:
                if (
                        "error" in item or
                        not item.get("batch_num") or
                        not item.get("expirydate") or
                        not item.get("po_num")
                ):
                    error_files.append(f"{folder_label}/{img_file}")
                    break

        return True

    folder_has_images = process_folder(selected_folder, os.path.basename(selected_folder))

    if not folder_has_images:
        for subdir_name in os.listdir(selected_folder):
            subdir_path = os.path.join(selected_folder, subdir_name)
            if os.path.isdir(subdir_path):
                process_folder(subdir_path, subdir_name)

    result_file = os.path.join(selected_folder, "OCR_results.txt")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        f.write("\n\n=== 統計資訊 ===\n")
        f.write(f"共 {len(error_files)} 個檔案有錯誤或缺欄位：\n")
        for err_file in error_files:
            f.write(f"✘ {err_file}\n")

    print(f"\n所有結果已儲存至：{result_file}")
    print("\n=== 統計資訊 ===")
    print(f"共 {len(error_files)} 個檔案有錯誤或缺欄位：")
    for err_file in error_files:
        print(f"✘ {err_file}")

if __name__ == "__main__":
    main()
