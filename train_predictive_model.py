import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

# 1. Đọc và chuẩn bị dữ liệu
# Thêm dòng này để xem 5 dòng đầu tiên và tên các cột
df = pd.read_csv('sensor_data.csv')
print("Đã đọc file CSV thành công. Dưới đây là 5 dòng đầu tiên và tên các cột:")
print(df.head())
print("\nDanh sách các cột:", df.columns.tolist())
print("-" * 50)

df['timestamp'] = pd.to_datetime(df['timestamp'])

# 2. Feature Engineering: Tạo cột mục tiêu (target)
# SỬA Ở ĐÂY: Dùng 'soilMoisture' thay vì 'soil_moisture'
df['target_soilMoisture'] = df['soilMoisture'].shift(-180)
df.dropna(inplace=True)

# 3. Chọn Features và Target
# SỬA Ở ĐÂY: Sửa lại tên các cột features cho khớp với file CSV
features = ['temperature', 'humidity', 'lightIntensity']
target = 'target_soilMoisture'

X = df[features]
y = df[target]

# 4. Chia dữ liệu
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Huấn luyện mô hình
print("\nBắt đầu huấn luyện mô hình Random Forest...")
model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1) # n_jobs=-1 để dùng tất cả CPU core, nhanh hơn
model.fit(X_train, y_train)
print("...Huấn luyện hoàn tất!")

# 6. Đánh giá
score = model.score(X_test, y_test)
print(f"\nModel Score (R^2): {score:.4f}")
if score > 0.8:
    print("✅ Kết quả đánh giá tốt!")
else:
    print("⚠️ Kết quả đánh giá chưa cao, có thể cần thêm dữ liệu hoặc tinh chỉnh model.")

# 7. Lưu mô hình
joblib.dump(model, 'soil_moisture_predictor.joblib')
print("\n✅ Model đã được lưu thành công vào file 'soil_moisture_predictor.joblib'")