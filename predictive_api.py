from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# Tải mô hình đã được huấn luyện
model = joblib.load('soil_moisture_predictor.joblib')

@app.route('/predict/soil_moisture', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        # Dữ liệu đầu vào ví dụ: {"temperature": 30.5, "air_humidity": 65, "light_intensity": 30000}
        
        # Chuyển dữ liệu thành DataFrame để model có thể hiểu
        df_input = pd.DataFrame([data])
        
        prediction = model.predict(df_input)
        
        return jsonify({'predicted_soil_moisture_in_3h': round(prediction[0], 2)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5001, debug=True)