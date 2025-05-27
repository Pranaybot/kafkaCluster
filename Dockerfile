FROM python:3.11-slim

# Set Spark and Hadoop versions
ENV SPARK_VERSION=3.3.0
ENV HADOOP_VERSION=3
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Set working directory early
WORKDIR /app

# Install Java, Python build tools, and system dependencies
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk curl gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies inside /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Spark
RUN curl -L https://downloads.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    | tar -xz -C /opt/ && \
    ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark

# Set Spark environment
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

# Copy the rest of the project into /app
COPY . .
