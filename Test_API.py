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
url = "http://localhost:3003/po_vision"  # 替換為您的 API URL
# url = "https://www.kutech.tw:3000/po_vision"

# 編碼圖片並建立請求資料格式
image_path = r"C:\database\po_vision\yonfu\yf_01.jpg" # 替換為您的圖片路徑
base64_string = encode_image_to_base64(image_path)
guid = "0030679"  # 替換為您的 GUID

payload = {
    "Data": [
        {
            "base64": base64_string,
            "GUID": guid
        }
    ]
}

# 設定請求標頭
headers = {
    "Content-Type": "application/json"
}


# pfx_path = r"C:\Users\Administrator\Desktop\20241213130839.pfx"
# pfx_password = "user82822040"
# 發送 POST 請求並等待回傳結果
response = requests.post(url, headers=headers, data=json.dumps(payload))
# response = requests_pkcs12.post(url, headers=headers, data=json.dumps(payload), pkcs12_filename=pfx_path, pkcs12_password=pfx_password)

# 檢查回傳結果
if response.status_code == 200:
    # 解析回傳的 JSON 資料
    response_data = response.json()
    print("回傳資料：", json.dumps(response_data, indent=4, ensure_ascii=False))
else:
    print("API 請求失敗，狀態碼：", response.status_code)

image = cv2.imread(image_path)
response_data = response.json()
# 讀取所有的 coord 並在圖片上劃出框線

if "degree" in response_data["Data"][0]:
    degree = int(response_data["Data"][0]["degree"])
    if degree == 90:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif degree == 180:
        image = cv2.rotate(image, cv2.ROTATE_180)
    elif degree == 270:
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

for item in response_data["Data"]:
    for key, value in item.items():
        if key.endswith("_coord"):
            # 將文字坐標轉為整數並解析成多邊形頂點
            coord_points = [tuple(map(int, point.split(','))) for point in value.split(';')]
            # 在圖片上畫多邊形
            coord_array = np.array(coord_points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(image, [coord_array], isClosed=True, color=(0, 255, 0), thickness=1)

scale = 1

image =  cv2.resize(image,(0,0), fx=scale, fy=scale)

# cv2.imwrite("test.jpg", image)

cv2.imshow("output", image)
cv2.waitKey(0)
cv2.destroyAllWindows()