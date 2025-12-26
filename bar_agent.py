import time
import requests
import hmac
import hashlib
import json
import os
import datetime
from uuid import UUID

# Configuration
API_URL = "http://localhost:8000/ingest"
CSV_FILE = "current_log.csv"

# Mock Venues (Matches init_db.py)
VENUES = {
    "00000000-0000-0000-0000-000000000001": "secret_joe",     # Joe Kool's
    "00000000-0000-0000-0000-000000000002": "secret_barney",  # Barney's
    "00000000-0000-0000-0000-000000000003": "secret_molly",   # Molly Bloom's
    "00000000-0000-0000-0000-000000000004": "secret_ceeps",   # The Ceeps
    "00000000-0000-0000-0000-000000000005": "secret_toboggan" # Toboggan
}

def get_file_lines(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return f.readlines()

def parse_line(line):
    # CSV Format: timestamp,venue_id,quantity
    # Backward compat: timestamp,quantity -> uses Joe Kool's default
    parts = line.strip().split(',')
    
    if len(parts) == 3:
        return parts[0], parts[1], int(parts[2])
    elif len(parts) == 2:
        return parts[0], "00000000-0000-0000-0000-000000000001", int(parts[1])
    return None

def send_payload(timestamp_str, venue_id, count):
    if venue_id not in VENUES:
        print(f"Unknown Venue ID: {venue_id}")
        return

    secret_key = VENUES[venue_id]

    payload = {
        "venue_id": venue_id,
        "timestamp": timestamp_str, 
        "transaction_count": count
    }
    
    body = json.dumps(payload)
    
    # Sign
    signature = hmac.new(
        secret_key.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature
    }
    
    try:
        response = requests.post(API_URL, data=body, headers=headers)
        print(f"Sent: {payload} | Status: {response.status_code} | Resp: {response.text}")
    except Exception as e:
        print(f"Failed to send: {e}")

def main():
    print(f"Agent starting... Watching {CSV_FILE}...")
    
    last_pos = 0
    if os.path.exists(CSV_FILE):
        last_pos = os.path.getsize(CSV_FILE)

    while True:
        time.sleep(1)
        if not os.path.exists(CSV_FILE):
            continue
            
        current_size = os.path.getsize(CSV_FILE)
        if current_size > last_pos:
            with open(CSV_FILE, 'r') as f:
                f.seek(last_pos)
                new_lines = f.readlines()
                last_pos = f.tell()
                
            for line in new_lines:
                if not line.strip():
                    continue
                data = parse_line(line)
                if data:
                    ts, vid, qty = data
                    # Ensure TS is ISO format or compatible
                    if 'T' not in ts:
                         ts = datetime.datetime.now().isoformat()
                    send_payload(ts, vid, qty)

if __name__ == "__main__":
    # Write PID for process management
    pid_file = "/tmp/bar_agent.pid"
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))
        
    print(f"Bar Agent running (PID: {os.getpid()})")
    
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping agent...")
    finally:
        if os.path.exists(pid_file):
            os.remove(pid_file)
