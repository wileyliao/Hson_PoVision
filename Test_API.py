import requests
import json
import base64

def read_config():
    with open("Test_config.json", "r", encoding="utf-8") as f:
        raw_text = f.read()
    raw_text = raw_text.replace("\\", "/")
    return json.loads(raw_text)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        b64_string = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_string}"

config = read_config()
url = config.get("url")
image_path = config.get("image")

if not url:
    raise ValueError("❌ Test_config.json 中缺少 'url'")
if not image_path:
    raise ValueError("❌ Test_config.json 中缺少 'image'")

base64_string = encode_image_to_base64(image_path)

payload = {
    "Data": [
        {
            "base64": base64_string,
            "GUID": "0030679"
        }
    ]
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, headers=headers, data=json.dumps(payload))
if response.status_code == 200:
    print("回傳資料：", json.dumps(response.json(), indent=4, ensure_ascii=False))
else:
    print("API 請求失敗，狀態碼：", response.status_code)
