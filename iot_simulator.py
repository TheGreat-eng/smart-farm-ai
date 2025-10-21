import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import random

# ==================== CONFIGURATION ====================
# Sửa 'localhost' thành IP của máy chạy Backend nếu cần
BROKER = "localhost"
PORT = 1883
CLIENT_ID_PREFIX = "PythonSimulator"

# Định nghĩa các thiết bị bạn muốn mô phỏng
# Bạn có thể thêm nhiều thiết bị vào danh sách này
DEVICES = [
    {"id": "SOIL-001", "type": "SOIL_MOISTURE"},
    {"id": "DHT-001", "type": "AIR_HUMIDITY_TEMPERATURE"},
    {"id": "LIGHT-001", "type": "LIGHT_INTENSITY"}
]
# =======================================================

# --- Simulation Functions ---
def get_simulated_data(device_id, device_type):
    """Tạo ra một gói dữ liệu hoàn chỉnh cho một thiết bị."""
    hour = datetime.now().hour
    
    # Base values
    temp = 25.0 + (hour - 12) * 0.5 + random.uniform(-1, 1)
    air_humidity = 70.0 + random.uniform(-5, 5)
    soil_moisture = max(20, 75 - (datetime.now().minute * 0.8) + random.uniform(-2, 2))
    light = random.uniform(10, 100) if not (7 <= hour < 18) else random.uniform(15000, 45000)
    ph = 6.5 + random.uniform(-0.1, 0.1)

    payload = {
        "deviceId": device_id,
        "sensorType": device_type,
        "temperature": round(temp, 2),
        "humidity": round(air_humidity, 2), # Đổi tên 'air_humidity' thành 'humidity' để khớp
        "soilMoisture": round(soil_moisture, 2),
        "lightIntensity": round(light),
        "ph": round(ph, 2),
        "timestamp": datetime.now().isoformat()
    }
    return payload

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ MQTT Broker connected successfully!")
    else:
        print(f"❌ MQTT Connection failed with code: {rc}")

def on_publish(client, userdata, mid):
    # In ra ít thông tin hơn để tránh làm rối console
    # print(f"-> Message {mid} published.")
    pass

# --- Main Program ---
def run_simulator():
    client_id = f"{CLIENT_ID_PREFIX}-{random.randint(0, 1000)}"
    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        print(f"📡 Connecting to MQTT Broker at {BROKER}:{PORT}...")
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        time.sleep(2) # Chờ kết nối ổn định

        print("\n" + "="*50)
        print("🚀 SIMULATOR STARTED - Publishing data every 10 seconds.")
        print("Press Ctrl+C to stop.")
        print("="*50 + "\n")

        while True:
            for device in DEVICES:
                device_id = device["id"]
                device_type = device["type"]
                
                # Tạo topic và payload theo đúng quy tắc
                topic = f"sensor/{device_id}/data"
                payload = get_simulated_data(device_id, device_type)

                # Publish
                result = client.publish(topic, json.dumps(payload), qos=1)
                result.wait_for_publish() # Đảm bảo message được gửi đi

                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Published to {topic} for device {device_id}")
                else:
                    print(f"Failed to publish message to topic {topic}")
            
            print("-" * 20)
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n🛑 Simulator stopping...")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("🔌 Disconnected from MQTT Broker.")

if __name__ == '__main__':
    run_simulator()