import json
from collections import defaultdict
from kafka import KafkaConsumer
from datetime import datetime, timezone
from sqlalchemy import create_engine,text

consumer = KafkaConsumer(
    'ecommerce-events',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest',)

engine=create_engine("postgresql://warehouse:warehouse@localhost:5432/warehouse")
WINDOW_SECONDS=10

with engine.connect() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS analytics.streaming_stats(
        window_start TIMESTAMP,
        event_type TEXT,
        event_count INT)
        """))
    conn.commit()

window_counts = defaultdict(int)
window_start = datetime.now(timezone.utc)

print("Listeing for events..")
for message in consumer:
    event=message.value
    window_counts[event["event_type"]]+=1
    if (datetime.now(timezone.utc) - window_start).total_seconds() >= WINDOW_SECONDS:
        with engine.connect() as conn:
            for event_type, count in window_counts.items():
                conn.execute(
                    text("""INSERT INTO analytics.streaming_stats
                             (window_start, event_type, event_count)
                             VALUES (:ws, :et, :c)"""),
                    {"ws": window_start, "et": event_type, "c": count},
                )
            conn.commit()
        print(f"Flushed window {window_start}: {dict(window_counts)}")
        window_counts = defaultdict(int)
        window_start = datetime.now(timezone.utc)

    