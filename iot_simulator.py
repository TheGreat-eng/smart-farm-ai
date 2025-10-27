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
DEVICES = [
    {"id": "SOIL-001", "type": "SOIL_MOISTURE"},
    {"id": "DHT-001", "type": "AIR_HUMIDITY_TEMPERATURE"},
    {"id": "LIGHT-001", "type": "LIGHT_INTENSITY"}
]
# =======================================================

# --- Simulation Functions ---
def get_simulated_data(device_id, device_type):
    """Tạo ra một gói dữ liệu hoàn chỉnh cho một thiết bị."""
    now = datetime.now()
    hour = now.hour

    # Base values (giả lập theo thời gian)
    temp = 25.0 + (hour - 12) * 0.5 + random.uniform(-1, 1)
    air_humidity = 70.0 + random.uniform(-5, 5)
    soil_moisture = max(20, 75 - (now.minute * 0.8) + random.uniform(-2, 2))
    light = random.uniform(10, 100) if not (7 <= hour < 18) else random.uniform(15000, 45000)
    ph = 6.5 + random.uniform(-0.1, 0.1)

    payload = {
        "deviceId": device_id,
        "sensorType": device_type,
        "temperature": round(temp, 2),
        "humidity": round(air_humidity, 2),        # khớp key "humidity"
        "soilMoisture": round(soil_moisture, 2),
        "lightIntensity": int(round(light)),
        "ph": round(ph, 2),
        "timestamp": now.isoformat()
    }
    return payload

# --- MQTT Callbacks (API v1 style; dùng callback_api_version=4) ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ MQTT Broker connected successfully!")
    else:
        print(f"❌ MQTT Connection failed with code: {rc}")

def on_publish(client, userdata, mid):
    # Giữ console sạch
    pass

# --- Main Program ---
def run_simulator():
    client_id = f"{CLIENT_ID_PREFIX}-{random.randint(0, 1000000)}"

    # Quan trọng: chỉ định callback_api_version=4 để tương thích code cũ
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)

    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        print(f"📡 Connecting to MQTT Broker at {BROKER}:{PORT}...")
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        time.sleep(1.5)  # chờ kết nối ổn định

        print("\n" + "=" * 50)
        print("🚀 SIMULATOR STARTED - Publishing data every 10 seconds.")
        print("Press Ctrl+C to stop.")
        print("=" * 50 + "\n")

        while True:
            for device in DEVICES:
                device_id = device["id"]
                device_type = device["type"]

                topic = f"sensor/{device_id}/data"
                payload = get_simulated_data(device_id, device_type)
                data = json.dumps(payload, ensure_ascii=False)

                # QoS=1 và chờ publish hoàn tất để đảm bảo dữ liệu đến broker
                result = client.publish(topic, data, qos=1)
                result.wait_for_publish()

                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Published to {topic} for device {device_id}")
                else:
                    print(f"Failed to publish message to topic {topic} (rc={result.rc})")

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
