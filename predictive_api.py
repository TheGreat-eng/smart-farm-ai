from flask import Flask, request, jsonify
import joblib
import pandas as pd
from datetime import datetime
import requests
import warnings
import os

warnings.filterwarnings('ignore')

app = Flask(__name__)

# --- TẢI MODEL KHI KHỞI ĐỘNG SERVER ---
MODEL_PATH = 'soil_moisture_predictor.joblib'
if not os.path.exists(MODEL_PATH):
    print(f"LỖI: Không tìm thấy file model '{MODEL_PATH}'. Vui lòng chạy script training trước.")
    exit()

try:
    print("Đang tải model dự đoán...")
    model = joblib.load(MODEL_PATH)
    print("✅ Model đã được tải thành công!")
except Exception as e:
    print(f"Lỗi khi tải model: {e}")
    exit()

# --- CẤU HÌNH CHO GỢI Ý THÔNG MINH ---
SOIL_MOISTURE_THRESHOLD_LOW = 30.0
RAIN_THRESHOLD_MM = 2.0
WEATHER_API_KEY = "7884074a54f3d2baf0b79866f3edeb6c"
LATITUDE = 21.0285
LONGITUDE = 105.8542

# ... (Hàm get_weather_forecast giữ nguyên không đổi) ...
def get_weather_forecast():
    if not WEATHER_API_KEY or WEATHER_API_KEY == "7884074a54f3d2baf0b79866f3edeb6c":
        print("Cảnh báo: Thiếu API key của OpenWeatherMap. Bỏ qua kiểm tra thời tiết.")
        return 0, False
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LATITUDE}&lon={LONGITUDE}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        for forecast in data['list'][:2]:
            if 'rain' in forecast and '3h' in forecast['rain']:
                if forecast['rain']['3h'] > RAIN_THRESHOLD_MM:
                    return forecast['rain']['3h'], True
        return 0, False
    except Exception as e:
        print(f"Lỗi khi gọi API thời tiết: {e}")
        return 0, False

@app.route('/predict/soil_moisture', methods=['POST'])
def predict():
    try:
        input_data = request.get_json()
        features = {}
        
        current = input_data['current_data']
        historical = input_data['historical_data']

        # Lấy độ ẩm đất "hiện tại" (proxy từ 60 phút trước)
        current_soil_moisture_proxy = historical['soilMoisture_lag_60']

        # --- TẠO FEATURES ĐẦY ĐỦ ---
        features['soilMoisture'] = current_soil_moisture_proxy # Thêm feature mới
        features['temperature'] = current['temperature']
        features['humidity'] = current['humidity']
        features['lightIntensity'] = current['lightIntensity']
        
          # ... (Tạo các feature lag và rolling y như cũ) ...
        features['soilMoisture_lag_60'] = historical['soilMoisture_lag_60']
        features['temperature_lag_60'] = historical['temperature_lag_60']
        features['soilMoisture_lag_30'] = (historical['soilMoisture_lag_60'] + current_soil_moisture_proxy) / 2
        features['soilMoisture_lag_10'] = (historical['soilMoisture_lag_60'] + current_soil_moisture_proxy * 2) / 3
        features['temperature_lag_30'] = (historical['temperature_lag_60'] + current['temperature']) / 2
        features['temperature_lag_10'] = (historical['temperature_lag_60'] + current['temperature'] * 2) / 3
        features['soilMoisture_rolling_mean'] = historical['soilMoisture_rolling_mean_60m']
        features['temperature_rolling_mean'] = historical['temperature_rolling_mean_60m']
        features['lightIntensity_rolling_mean'] = historical['lightIntensity_rolling_mean_60m']
        now = datetime.now()
        features['hour'] = now.hour
        features['dayofweek'] = now.weekday()
        
        df_input = pd.DataFrame([features])
        feature_order = model.feature_names_in_
        df_input = df_input[feature_order]

        # --- DỰ ĐOÁN DELTA VÀ TÍNH TOÁN KẾT QUẢ CUỐI CÙNG ---
        predicted_delta = model.predict(df_input)[0]
        
        # Kết quả cuối cùng = Độ ẩm hiện tại + Sự thay đổi dự đoán
        predicted_moisture = current_soil_moisture_proxy + predicted_delta

        # ... (Phần logic gợi ý giữ nguyên không đổi) ...
        rain_amount, is_raining_soon = get_weather_forecast()
        suggestion = "Không cần hành động."
        action = "NONE"
        if is_raining_soon:
            suggestion = f"Dự báo có mưa ({rain_amount}mm). Tạm thời không cần tưới để tiết kiệm nước."
            action = "SKIP_IRRIGATION"
        elif predicted_moisture < SOIL_MOISTURE_THRESHOLD_LOW:
            suggestion = f"Độ ẩm đất dự kiến sẽ giảm xuống dưới ngưỡng {SOIL_MOISTURE_THRESHOLD_LOW}%. Nên lên lịch tưới."
            action = "SCHEDULE_IRRIGATION"
        
        return jsonify({
            'predicted_soil_moisture_in_3h': round(predicted_moisture, 2),
            'predicted_delta': round(predicted_delta, 2), # Trả về thêm delta để debug
            'suggestion': suggestion,
            'action': action,
            'weather_info': f"Rain forecast ({rain_amount}mm), Raining soon: {is_raining_soon}"
        })
    # except KeyError as e:
    #     return jsonify({'error': f"Thiếu trường dữ liệu trong JSON đầu vào: {e}"}), 400
    # except Exception as e:
    #     return jsonify({'error': f"Đã xảy ra lỗi: {e}"}), 500
    except Exception as e:
        return jsonify({'error': f"Đã xảy ra lỗi: {e}"}), 500


if __name__ == '__main__':
    app.run(port=5001, debug=True)