from flask import Flask, request, jsonify
from OCR_main import po_vision_main
from OCR_img_utils import base64_decoder
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

prefix = "data:image/jpeg;base64,"

app = Flask(__name__)

@app.route('/po_vision', methods=['POST'])
@app.route('/Po_Vision', methods=['POST'])
def po_vision_app():
    start_time = time.time()
    try:
        # 在處理每個請求之前，清空之前的日誌內容
        log_stream.seek(0)
        log_stream.truncate(0)
        data = request.json['Data'][0]
        guid = data.get('GUID')
        logging.info(f'Received api request: {guid}')

        # 處理前贅字樣
        image = base64_decoder(data.get('base64')[len(prefix):])
        logging.info(f'Start Main analyzing: {guid}')
        ocr_result, batch_expiry_checker, degree = po_vision_main(image)

        end_time = time.time()
        time_taken = end_time - start_time
        log_contents = log_stream.getvalue()

        final_list=[]
        for i in range(len(ocr_result)):
            data_dict={
                'GUID': guid,
                'logs': log_contents,
                **ocr_result[i]
            }
            final_list.append(data_dict)
        response_data = {
            'Data': final_list,
            'Degree': degree,
            'Code': 200,
            'Result': batch_expiry_checker,
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
                    'logs': log_contents
                }
            ],
            'Code': 200,
            'Result': 'False',
            'TimeTaken': f'{time_taken:.2f}秒'
        }

        print(log_contents)
        return jsonify(error_response), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3003, debug=True)
