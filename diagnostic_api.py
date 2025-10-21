from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
import cv2 # OpenCV
import json
import os

app = Flask(__name__)

# --- Tải Model và các file cần thiết một lần khi server khởi động ---
MODEL_PATH = 'plant_disease_model.h5'
CLASSES_PATH = 'class_indices.json'

# Kiểm tra xem file có tồn tại không
if not os.path.exists(MODEL_PATH) or not os.path.exists(CLASSES_PATH):
    print("="*50)
    print("LỖI: Không tìm thấy file 'plant_disease_model.h5' hoặc 'class_indices.json'")
    print("Vui lòng đảm bảo 2 file này nằm cùng thư mục với script API.")
    print("="*50)
    exit()

try:
    print("Đang tải model TensorFlow... Quá trình này có thể mất một lúc.")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("✅ Model đã được tải thành công!")

    with open(CLASSES_PATH, 'r') as f:
        class_indices = json.load(f)
    # Đảo ngược key-value để map từ index -> tên lớp
    class_names = {v: k for k, v in class_indices.items()}
    print("✅ Danh sách lớp đã được tải thành công!")

except Exception as e:
    print(f"Lỗi khi tải model: {e}")
    exit()
# -----------------------------------------------------------------


def preprocess_image(image_bytes):
    """Hàm tiền xử lý ảnh trước khi đưa vào model"""
    try:
        # Đọc ảnh từ byte stream
        image_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Chuyển từ BGR (mặc định của OpenCV) sang RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize về đúng kích thước đầu vào của model (224x224)
        image = cv2.resize(image, (224, 224))
        
        # Chuẩn hóa giá trị pixel về khoảng [0, 1]
        image = image / 255.0
        
        # Mở rộng chiều để phù hợp với input của model (từ (224,224,3) -> (1, 224, 224, 3))
        image = np.expand_dims(image, axis=0)
        return image
    except Exception as e:
        print(f"Lỗi tiền xử lý ảnh: {e}")
        return None

@app.route('/diagnose', methods=['POST'])
def diagnose():
    if 'image' not in request.files:
        return jsonify({'error': 'Không có file ảnh nào được gửi lên (trường "image" bị thiếu)'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'Tên file trống'}), 400

    try:
        image_bytes = file.read()
        processed_image = preprocess_image(image_bytes)
        
        if processed_image is None:
            return jsonify({'error': 'File ảnh không hợp lệ hoặc bị lỗi'}), 400

        # Dự đoán
        predictions = model.predict(processed_image)
        
        # Lấy lớp có xác suất cao nhất
        predicted_class_index = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0]))
        
        # Lấy tên lớp
        class_name_raw = class_names[predicted_class_index]
        
        # Làm đẹp tên lớp để trả về cho người dùng
        # Ví dụ: "Tomato___Late_blight" -> "Tomato - Late blight"
        class_name_formatted = class_name_raw.replace('___', ' - ').replace('_', ' ')
        
        return jsonify({
            'disease': class_name_formatted,
            'confidence': f"{confidence:.2%}"
        })
    except Exception as e:
        print(f"Lỗi trong quá trình dự đoán: {e}")
        return jsonify({'error': 'Đã xảy ra lỗi không xác định trên server'}), 500

if __name__ == '__main__':
    # Chạy trên cổng 5002 để không trùng với API dự đoán
    app.run(host='0.0.0.0', port=5002, debug=True)