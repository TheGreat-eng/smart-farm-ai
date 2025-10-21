import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np

print("Generating fake sensor data...")

# Cấu hình
NUM_DAYS = 20  # Tạo dữ liệu cho 20 ngày
SAMPLES_PER_HOUR = 60 # Dữ liệu mỗi phút
TOTAL_SAMPLES = NUM_DAYS * 24 * SAMPLES_PER_HOUR
START_TIME = datetime.now() - timedelta(days=NUM_DAYS)

# Tạo chuỗi thời gian
timestamps = [START_TIME + timedelta(minutes=i) for i in range(TOTAL_SAMPLES)]

# Tạo dữ liệu giả lập
data = []
for ts in timestamps:
    hour = ts.hour
    
    # Mô phỏng nhiệt độ theo chu kỳ ngày đêm
    temp = 25.0 + 5 * np.sin(np.pi * (hour - 8) / 12) + random.uniform(-1, 1)
    
    # Mô phỏng độ ẩm không khí
    humidity = 70.0 - 10 * np.sin(np.pi * (hour - 8) / 12) + random.uniform(-5, 5)
    
    # Mô phỏng độ ẩm đất (giảm dần và được "tưới" ngẫu nhiên)
    # Cứ mỗi 6 giờ lại có khả năng được tưới
    if ts.hour % 6 == 0 and ts.minute == 0:
        soil_moisture = 80.0
    else:
        # Giảm dần tự nhiên
        try:
            soil_moisture = data[-1]['soilMoisture'] - 0.15 + random.uniform(-0.1, 0.1)
        except IndexError:
            soil_moisture = 75.0
    soil_moisture = max(20, min(90, soil_moisture))

    # Mô phỏng ánh sáng
    light = max(0, 50000 * np.sin(np.pi * (hour - 6) / 13)) + random.uniform(0, 1000) if 6 < hour < 19 else random.uniform(0, 50)
    
    data.append({
        'timestamp': ts.isoformat(),
        'deviceId': 'SOIL-001',
        'temperature': round(temp, 2),
        'humidity': round(humidity, 2),
        'soilMoisture': round(soil_moisture, 2),
        'lightIntensity': round(light),
    })

# Tạo DataFrame và lưu ra CSV
df = pd.DataFrame(data)
df.to_csv('sensor_data.csv', index=False)

print(f"Successfully generated 'sensor_data.csv' with {len(df)} rows.")