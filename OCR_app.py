from flask import Flask, request, jsonify
from OCR_img_utils import base64_decoder, cut_roi_from_image
from OCR_main import po_vision_main
import logging
import io
import time


# 禁用 PaddleOCR 的日誌輸出
class NoOutputFilter(logging.Filter):
    def filter(self, record):
        return False


paddle_logger_ppocr = logging.getLogger('ppocr')
paddle_logger_ppocr.setLevel(logging.CRITICAL)
paddle_logger_ppocr.addFilter(NoOutputFilter())


# 創建內存中的日誌流
log_stream = io.StringIO()
stream_handler = logging.StreamHandler(log_stream)
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)

# 設置global log日誌
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[stream_handler]  # 使用內存流處理器
)
# 手動設置根 logger 級別
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.handlers = [stream_handler]

# 設置 werkzeug logger 級別(for flask)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.DEBUG)

keywords = [
    "PONO",
    "PRODUCT",
    "QUANTITY",
    "BATCH NUMBER",
    "EXPIRYDATE"
]

prefix = "data:image/jpeg;base64,"

app = Flask(__name__)
@app.route('/PO_Vision', methods = ['POST'])
def po_vision_app():
    start_time = time.time()
    try:
        # 在處理每個請求之前，清空之前的日誌內容
        log_stream.seek(0)
        log_stream.truncate(0)
        data = request.json['Data'][0]
        guid = data.get('GUID')
        logging.info(f'Received api request: {guid}')

        """處理前墜"""
        base64_image = data.get('base64')
        prefix_length = len(prefix)
        clean_base64_image = base64_image[prefix_length:]
        image = base64_decoder(clean_base64_image)
        """處理前墜"""

        ocr_result = po_vision_main(
            cut_roi_from_image(image, y_top_ratio=0.2, y_bottom_ratio=0.4),
            keywords
        )
        end_time = time.time()
        time_taken = end_time - start_time
        log_contents = log_stream.getvalue()

        response_data = {
            'Data': [
                {
                    'GUID': guid,
                    'logs': log_contents,
                    'op_keywords': (','.join(keywords)),
                    **ocr_result
                }
            ],
            'Code': 200,
            'Result': 'True',
            'TimeTaken': f'{time_taken:.2f}秒'
        }

        print(log_contents)
        return jsonify(response_data), 200

    except Exception as e:
        end_time = time.time()
        time_taken = end_time - start_time
        logging.error(e)
        log_contents = log_stream.getvalue()
        error_response = {
            "Data": [
                {
                    'GUID': guid,
                    'logs': log_contents,
                    'op_keywords': (','.join(keywords))
                }
            ],
            'Code': 200,
            'Result': 'False',
            'TimeTaken': f'{time_taken:.2f}秒'
        }

        print(log_contents)
        return jsonify(error_response), 500


if __name__ == '__main__':
    app.run(port=5000)
