import os
import requests
import json
import pandas as pd

# -------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------
FAST2SMS_API_KEY = "kzlLbqxGhRY4Qv73dOUuBKgX2y1IDirJws9mWtP8VZN56C0MHcmMlUqrb38vuITZoxeRAWF2y9s7OVd4"
TARGET_PHONES = "7200326418,9489208429,9176938490"

def send_dispatch_sms(api_key: str = FAST2SMS_API_KEY, target_phones: str = TARGET_PHONES):
    notif_file = os.path.join("output", "notification_output.csv")
    if not os.path.exists(notif_file):
        print("[ERROR] 'output/notification_output.csv' not found. Run 'python main.py' first.")
        return

    df_notif = pd.read_csv(notif_file)
    row = df_notif.iloc[0]

    # Safe extraction with fallback defaults
    worker_name = row.get("worker_name", "Field Technician")
    urgency = row.get("urgency", "High")
    location = row.get("target_location", "Velachery Area")
    node = row.get("target_node", "N007")
    priority = row.get("priority_score", 90)
    route = row.get("safe_path", "Direct Navigation Path")
    distance = row.get("safe_distance_m", 0.0)

    url = "https://www.fast2sms.com/dev/bulkV2"
    
    # Message formatted for mobile delivery
    message_text = (
        f"URGENT FLOOD ALERT: {worker_name} dispatched to {location} ({node}). "
        f"Priority: {priority}/100. Safe Route: {route}. Distance: {distance}m"
    )

    print("=" * 80)
    print(f"HydroGraph-Twin — Dispatching SMS to {target_phones}")
    print("=" * 80)
    print(f"Payload: {message_text}\n")

    headers = {
        "authorization": api_key.strip(),
        "Content-Type": "application/json"
    }

    payload = {
        "route": "q",
        "message": message_text,
        "language": "english",
        "numbers": target_phones.strip()
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        res_data = response.json()
        print("Gateway Response:", res_data)
        
        if res_data.get("return") is True:
            print("\n[SUCCESS] SMS successfully delivered to all 3 mobile phones!")
        else:
            print(f"\n[NOTE] Gateway status: {res_data.get('message')}")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")

if __name__ == "__main__":
    send_dispatch_sms()