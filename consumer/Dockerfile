FROM bitnami/spark:3.4.1

COPY kafka_consumer.py /opt/spark-apps/kafka_consumer.py

ENTRYPOINT ["/opt/bitnami/scripts/spark/entrypoint.sh"]

CMD ["spark-submit", "/opt/spark-apps/kafka_consumer.py"]
