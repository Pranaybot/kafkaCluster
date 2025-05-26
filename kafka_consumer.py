import os
import csv
import time
from confluent_kafka import Consumer, KafkaError

def get_next_filename(messages_dir):
    if not os.path.exists(messages_dir):
        os.makedirs(messages_dir)
    existing_files = [f for f in os.listdir(messages_dir) if f.startswith("file_") and f.endswith(".csv")]
    next_index = len(existing_files) + 1
    return os.path.join(messages_dir, f"file_{next_index}.csv")

def consume_messages(batch_size, bootstrap_servers, topic_name, output_dir):
    consumer = Consumer({
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'my-group',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe([topic_name])
    messages = []

    filename = get_next_filename(output_dir)
    print(f"Saving consumed messages to: {filename}")

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['message'])

        while len(messages) < batch_size:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Error: {msg.error()}")
                    break
            message_value = msg.value().decode('utf-8')
            writer.writerow([message_value])
            messages.append(message_value)
            print(f"Consumed: {message_value}")

    consumer.close()

if __name__ == "__main__":
    bootstrap_servers = 'kafka-1:9092,kafka-2:9093,kafka-3:9094'
    topic_name = 'second_test'
    output_dir = './messages'

    time.sleep(5)  # Optional safety delay
    consume_messages(1000, bootstrap_servers, topic_name, output_dir)
