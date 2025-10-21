import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np

print("Generating ADVANCED fake sensor data...")

# Cấu hình
NUM_DAYS = 30  # Tăng số ngày dữ liệu lên 30 ngày
SAMPLES_PER_HOUR = 60 # Dữ liệu mỗi phút
TOTAL_SAMPLES = NUM_DAYS * 24 * SAMPLES_PER_HOUR
START_TIME = datetime.now() - timedelta(days=NUM_DAYS)

timestamps = [START_TIME + timedelta(minutes=i) for i in range(TOTAL_SAMPLES)]

data = []
# Khởi tạo độ ẩm đất ban đầu
current_soil_moisture = 75.0

for ts in timestamps:
    hour = ts.hour
    
    # === MÔ PHỎNG NÂNG CAO ===
    # 1. Nhiệt độ & Ánh sáng (có mối liên quan)
    # Dùng hàm sin để tạo chu kỳ ngày đêm mượt mà
    temp = 24.0 + 8 * np.sin(np.pi * (hour - 8) / 14) + random.uniform(-0.5, 0.5)
    light = max(0, 50000 * np.sin(np.pi * (hour - 7) / 13)) + random.uniform(0, 500) if 7 < hour < 20 else random.uniform(0, 20)
    humidity = 80.0 - 20 * np.sin(np.pi * (hour - 6) / 15) + random.uniform(-5, 5)

    # 2. Độ ẩm đất (BỊ ẢNH HƯỞNG BỞI NHIỆT ĐỘ VÀ ÁNH SÁNG)
    # Yếu tố bay hơi, phụ thuộc vào nhiệt độ và ánh sáng
    evaporation_rate = (temp / 30) * 0.05 + (light / 50000) * 0.1
    current_soil_moisture -= evaporation_rate
    
    # Mô phỏng việc tưới nước ngẫu nhiên để reset độ ẩm
    if random.random() < 0.01: # 1% cơ hội được tưới mỗi phút
        current_soil_moisture = random.uniform(80, 90)

    # Thêm nhiễu và đảm bảo trong khoảng hợp lệ
    soil_moisture_with_noise = current_soil_moisture + random.uniform(-0.5, 0.5)
    current_soil_moisture = max(15, min(95, soil_moisture_with_noise))

    data.append({
        'timestamp': ts.isoformat(),
        'deviceId': 'SOIL-001',
        'temperature': round(temp, 2),
        'humidity': round(humidity, 2),
        'soilMoisture': round(current_soil_moisture, 2),
        'lightIntensity': round(light),
    })

df = pd.DataFrame(data)
df.to_csv('sensor_data.csv', index=False)

print(f"Successfully generated 'sensor_data.csv' with {len(df)} rows.")