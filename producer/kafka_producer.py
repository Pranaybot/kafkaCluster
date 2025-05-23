import os
from kafka import KafkaProducer
from faker import Faker
import json
import time
import uuid

faker = Faker()
kafka_brokers = os.environ.get("KAFKA_BROKERS", "kafka1:29092").split(",")
print("Kafka Brokers:", kafka_brokers)

producer = KafkaProducer(
    bootstrap_servers=kafka_brokers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic = 'user-messages'

def generate_message():
    return {
        "id": str(uuid.uuid4()),
        "name": faker.name(),
        "text_message": faker.sentence()
    }

if __name__ == "__main__":
    for _ in range(1000):
        msg = generate_message()
        producer.send(topic, value=msg)
        print(f"Sent: {msg}")
        time.sleep(0.01)
    producer.flush()
