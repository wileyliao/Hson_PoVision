import os
from PIL import Image
from pillow_heif import register_heif_opener

# 註冊 HEIF 支援
register_heif_opener()


def convert_heic_to_jpg(folder_path):
    # 取得資料夾中的所有 HEIC 檔案
    files = [f for f in os.listdir(folder_path) if f.lower().endswith('.heic')]
    files.sort()  # 確保轉換順序穩定

    for idx, file in enumerate(files, start=1):
        heic_file_path = os.path.join(folder_path, file)
        new_file_name = f"{str(idx).zfill(2)}.jpg"  # 01.jpg, 02.jpg...
        jpg_file_path = os.path.join(folder_path, new_file_name)

        # 開啟 HEIC 圖片並轉換為 JPG
        with Image.open(heic_file_path) as img:
            img = img.convert("RGB")  # 確保轉換為 RGB 格式
            img.save(jpg_file_path, "JPEG")
            print(f"Converted {file} to {new_file_name}")


# 指定資料夾路徑
folder_path = r"C:\python\Hson_PoVision\rotate_img"
convert_heic_to_jpg(folder_path)
