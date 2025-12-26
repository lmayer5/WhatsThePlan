import time
import os
import redis
import json
import datetime
import socket
import signal
import sys
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app import models, database

# Config
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/venues_db")
STREAM_KEY = "stream:incoming_txns"
GROUP_NAME = "workers_group"
CONSUMER_NAME = f"worker_{socket.gethostname()}"
DLQ_KEY = "stream:dlq"
MAX_RETRIES = 3

# Connections
redis_client = redis.from_url(REDIS_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Global flag for graceful shutdown
SHUTDOWN = False

def signal_handler(sig, frame):
    global SHUTDOWN
    print("Shutdown signal received. Finishing current job...")
    SHUTDOWN = True

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def ensure_group():
    try:
        redis_client.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
        print(f"Created consumer group {GROUP_NAME}")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print(f"Consumer group {GROUP_NAME} already exists")
        else:
            raise e

def calculate_hotness(db, venue_id):
    # Hotness = (Sum txns last 30 mins / Capacity) * 100
    venue = db.query(models.Venue).filter(models.Venue.id == venue_id).first()
    if not venue:
        print(f"Venue {venue_id} not found")
        return 0

    thirty_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
    
    total_txns = db.query(func.sum(models.Transaction.quantity))\
        .filter(models.Transaction.venue_id == venue_id)\
        .filter(models.Transaction.timestamp >= thirty_mins_ago)\
        .scalar() or 0

    if venue.capacity == 0:
        return 0

    score = int((total_txns / venue.capacity) * 100)
    return min(score, 100)

def handle_poison_pill(id, message, error):
    print(f"Moving dangerous message {id} to DLQ due to: {error}")
    # Push to DLQ List or Stream. Using List for simplicity here
    redis_client.lpush(DLQ_KEY, json.dumps({"id": id, "message": str(message), "error": str(error)}))
    # Ack to remove from main stream
    redis_client.xack(STREAM_KEY, GROUP_NAME, id)

def process_message(id, message):
    db = SessionLocal() # Session per message
    try:
        data = message
        # Handle Byte decoding
        venue_id = data.get(b'venue_id') or data.get('venue_id')
        timestamp_str = data.get(b'timestamp') or data.get('timestamp')
        qty = data.get(b'transaction_count') or data.get('transaction_count')
        
        if isinstance(venue_id, bytes): venue_id = venue_id.decode('utf-8')
        if isinstance(timestamp_str, bytes): timestamp_str = timestamp_str.decode('utf-8')
        if isinstance(qty, bytes): qty = int(qty)
        else: qty = int(qty)

        # 1. Persist
        new_txn = models.Transaction(
            venue_id=venue_id,
            timestamp=datetime.datetime.fromisoformat(timestamp_str),
            quantity=qty
        )
        db.add(new_txn)
        db.commit()
        print(f"Persisted txn for {venue_id}: {qty}")

        # 2. Calculate Hotness
        score = calculate_hotness(db, venue_id)
        print(f"Hotness for {venue_id}: {score}%")

        # 3. Update Redis Key
        redis_client.set(f"venue:{venue_id}:score", score)

        # 4. Publish Update
        pub_msg = json.dumps({"venue_id": venue_id, "score": score})
        redis_client.publish("updates:venue_scores", pub_msg)

        # Ack
        redis_client.xack(STREAM_KEY, GROUP_NAME, id)
        
        # Clear retry counter if successful
        redis_client.delete(f"retry:{id}")

    except Exception as e:
        print(f"Error processing message {id}: {e}")
        db.rollback()
        
        # Retry Logic
        retry_key = f"retry:{id}"
        retries = redis_client.incr(retry_key)
        if retries > MAX_RETRIES:
            handle_poison_pill(id, message, e)
            redis_client.delete(retry_key)
        else:
            print(f"Message {id} failed {retries}/{MAX_RETRIES} times. Will be redelivered.")
            # Do NOT ack, so it will be picked up again (or claimed by another consumer)
            # In a real system, you might want to use XCLAIM or rely on visibility timeout
            
    finally:
        db.close()

def main():
    print(f"Worker {CONSUMER_NAME} starting...")
    ensure_group()
    
    while not SHUTDOWN:
        try:
            # Read new messages with block to prevent busy loop
            streams = redis_client.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: ">"}, count=1, block=2000)
            
            if streams:
                for stream_name, messages in streams:
                    for id, message in messages:
                        process_message(id, message)
            
            # TODO: Add logic here to occasionally check for pending messages (PEL) from crashed workers
            # that haven't been acked for a long time (XPENDING + XCLAIM)
            
        except Exception as e:
            print(f"Worker Loop Error: {e}")
            time.sleep(5)
            
    print("Worker shutdown complete.")

if __name__ == "__main__":
    main()
