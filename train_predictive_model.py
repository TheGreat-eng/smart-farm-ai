import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
import joblib
import warnings

warnings.filterwarnings('ignore')

print("\n" + "="*60)
print("🚀 ADVANCED MODEL TRAINING & COMPARISON 🚀")
print("="*60)

try:
    print("\n[Step 1/4] Loading and preparing data...")
    df = pd.read_csv('sensor_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # === NEW FEATURE ENGINEERING APPROACH ===
    print("   - Creating NEW target variable (Delta Soil Moisture)...")

    # TÍNH TOÁN SỰ THAY ĐỔI (DELTA) THAY VÌ GIÁ TRỊ TUYỆT ĐỐI
    future_soil_moisture = df['soilMoisture'].shift(-180)
    df['delta_soilMoisture_3h'] = future_soil_moisture - df['soilMoisture']

    # Bỏ qua những thay đổi phi lý do tưới nước (những cú nhảy vọt dương)
    # Chúng ta chỉ muốn model học sự bay hơi (giảm đi)
    df = df[df['delta_soilMoisture_3h'] <= 5] # Cho phép sai số dương nhỏ

    # Tạo các features như cũ
    for lag in [10, 30, 60]:
        df[f'soilMoisture_lag_{lag}'] = df['soilMoisture'].shift(lag)
        df[f'temperature_lag_{lag}'] = df['temperature'].shift(lag)
    window_size = 60
    df['soilMoisture_rolling_mean'] = df['soilMoisture'].shift(1).rolling(window=window_size).mean()
    df['temperature_rolling_mean'] = df['temperature'].shift(1).rolling(window=window_size).mean()
    df['lightIntensity_rolling_mean'] = df['lightIntensity'].shift(1).rolling(window=window_size).mean()
    df['hour'] = df['timestamp'].dt.hour
    df['dayofweek'] = df['timestamp'].dt.dayofweek
    
    df.dropna(inplace=True)
    
    print(f"✅ Data ready with {len(df)} valid rows.")
    
    # CHỌN FEATURES VÀ TARGET MỚI
    features = [
        # Thêm độ ẩm đất hiện tại vào features vì nó rất quan trọng để dự đoán delta
        'soilMoisture', 
        'temperature', 'humidity', 'lightIntensity',
        'soilMoisture_lag_10', 'soilMoisture_lag_30', 'soilMoisture_lag_60',
        'temperature_lag_10', 'temperature_lag_30', 'temperature_lag_60',
        'soilMoisture_rolling_mean', 'temperature_rolling_mean', 'lightIntensity_rolling_mean',
        'hour', 'dayofweek'
    ]
    target = 'delta_soilMoisture_3h' # <--- TARGET MỚI
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"✅ Data split: {len(X_train)} train, {len(X_test)} test rows.")

except Exception as e:
    print(f"\n❌ AN ERROR OCCURRED: {e}")
    exit()

# ... (Phần huấn luyện và so sánh giữ nguyên y hệt)
# ... (Nó sẽ tự động dùng bộ features X và y mới)

print("\n[Step 2/4] Starting training and comparison of 3 algorithms...")
models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(random_state=42),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
}
results = {}
for name, model in models.items():
    print(f"   - Training {name}...")
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    results[name] = score
    print(f"     -> Done! R^2 Score: {score:.4f}")

print("\n[Step 3/4] Displaying comparison results...")
print("\n" + "="*60)
print("📊 ALGORITHM PERFORMANCE COMPARISON (R-squared Score) 📊")
print("="*60)
best_model_name = max(results, key=results.get)
for name, score in sorted(results.items(), key=lambda item: item[1], reverse=True):
    is_best = "🏆 (Best Choice)" if name == best_model_name else ""
    print(f"   - {name:<20}: {score:.4f} {is_best}")

print("\n[Step 4/4] Saving the best performing model...")
best_model_instance = models[best_model_name]
joblib.dump(best_model_instance, 'soil_moisture_predictor.joblib')
print(f"✅ Model '{best_model_name}' saved to 'soil_moisture_predictor.joblib'")

print("\n" + "="*60)
print("🎉 PROCESS COMPLETE! 🎉")
print("="*60)