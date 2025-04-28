import requests
import json
import base64
import cv2
import numpy as np

# 將圖片轉為 Base64 字串（假設圖片路徑為 'image.jpg'）
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        b64_string = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_string}"

# 設定要傳送的 API URL
url = "http://localhost:3003/Po_Vision"  # 替換為您的 API URL
# url = "https://www.kutech.tw:3000/Po_Vision"  # 替換為您的 API URL

image_path = r"C:\database\po_vision\大昌\dk_01.jpg"
base64_string = encode_image_to_base64(image_path)

payload = {
    "Data": [
        {
            "base64": base64_string,
            "GUID": "0030679"
        }
    ]
}

# 設定請求標頭
headers = {
    "Content-Type": "application/json"
}

# 發送 POST 請求並等待回傳結果
response = requests.post(url, headers=headers, data=json.dumps(payload))

# 檢查回傳結果
if response.status_code == 200:
    # 解析回傳的 JSON 資料
    response_data = response.json()
    print("回傳資料：", json.dumps(response_data, indent=4, ensure_ascii=False))
else:
    print("API 請求失敗，狀態碼：", response.status_code)
