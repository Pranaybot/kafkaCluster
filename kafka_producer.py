import time
from faker import Faker
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer

def wait_for_kafka(servers, timeout=30):
    start_time = time.time()
    while True:
        try:
            admin_client = AdminClient({'bootstrap.servers': servers})
            metadata = admin_client.list_topics(timeout=5)
            print("Kafka is available.")
            break
        except Exception:
            if time.time() - start_time > timeout:
                raise RuntimeError("Kafka did not become available in time.")
            print("Waiting for Kafka to be available...")
            time.sleep(2)

def create_topic(bootstrap_servers, topic_name):
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    new_topic = NewTopic(topic_name, num_partitions=3, replication_factor=3)
    fs = admin_client.create_topics([new_topic])
    for topic, f in fs.items():
        try:
            f.result()
            print(f"Topic '{topic}' created.")
        except Exception as e:
            print(f"Topic '{topic}' exists or failed to create: {e}")

def produce_fake_messages(n, bootstrap_servers, topic_name):
    fake = Faker()
    producer = Producer({'bootstrap.servers': bootstrap_servers})
    for _ in range(n):
        msg = fake.sentence()
        producer.produce(topic_name, msg.encode('utf-8'))
        print(f"Produced: {msg}")
    producer.flush()

if __name__ == "__main__":
    bootstrap_servers = 'kafka-1:9092,kafka-2:9093,kafka-3:9094'
    topic_name = 'second_test'

    wait_for_kafka(bootstrap_servers)
    create_topic(bootstrap_servers, topic_name)
    produce_fake_messages(1000, bootstrap_servers, topic_name)
