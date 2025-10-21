from flask import Flask, request, jsonify

app = Flask(__name__)

def check_fungus_risk(data):
    """Quy tắc 1: Nguy cơ nấm"""
    # Giả sử data có thêm trường 'duration_high_humidity_hr' (số giờ độ ẩm cao liên tục)
    # Backend sẽ cần tính toán và gửi trường này
    if data.get('humidity', 0) > 85 and 20 <= data.get('temperature', 0) <= 28 and data.get('duration_high_humidity_hr', 0) > 48:
        return {
            "risk_level": "HIGH",
            "warning_code": "FUNGUS_RISK",
            "message": "Cảnh báo nguy cơ nấm phát triển cao do độ ẩm và nhiệt độ lý tưởng kéo dài.",
            "suggestion": "Tăng cường thông gió, giảm tưới và kiểm tra cây trồng."
        }
    return None

def check_heat_stress(data):
    """Quy tắc 2: Stress nhiệt"""
    # Giả sử có trường 'duration_high_temp_hr'
    if data.get('temperature', 0) > 38 and data.get('duration_high_temp_hr', 0) > 4:
        return {
            "risk_level": "MEDIUM",
            "warning_code": "HEAT_STRESS",
            "message": "Nhiệt độ quá cao và kéo dài, cây có thể bị stress nhiệt.",
            "suggestion": "Cân nhắc phun sương, che chắn và tưới nhẹ."
        }
    return None

# ... (Viết thêm các hàm cho 5 quy tắc còn lại)

ALL_RULES = [
    check_fungus_risk,
    check_heat_stress,
    # ...
]

@app.route('/check_rules', methods=['POST'])
def check_all_rules():
    try:
        current_data = request.get_json()
        warnings = []
        
        for rule_function in ALL_RULES:
            result = rule_function(current_data)
            if result:
                warnings.append(result)
        
        if not warnings:
            return jsonify({
                "status": "OK",
                "message": "Tất cả các chỉ số đều trong ngưỡng an toàn."
            })
        
        return jsonify({
            "status": "WARNING",
            "warnings": warnings
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5003, debug=True) # Chạy trên cổng 5003