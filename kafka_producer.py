import sys
import six

if sys.version_info >= (3, 12, 7): 
    sys.modules['kafka.vendor.six.moves'] = six.moves

import json
import requests
from kafka import KafkaProducer
from typing import Iterator, Dict, Any
import logging
import time


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092' 
KAFKA_TOPIC = 'streaming_data'
API_URL = 'http://streaming-api:8000/stream'
MAX_RETRIES = 5
RETRY_DELAY = 10

class StreamProducer:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.topic = topic
        self.connect_with_retry(bootstrap_servers)

    def connect_with_retry(self, bootstrap_servers: str):
        """Connexion à Kafka avec retry"""
        retries = 0
        while retries < MAX_RETRIES:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=bootstrap_servers,
                    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                    key_serializer=str.encode,
                    api_version=(2, 5, 0)
                )
                logger.info("Connexion à Kafka établie avec succès")
                return
            except Exception as e:
                retries += 1
                logger.warning(f"Tentative {retries}/{MAX_RETRIES} de connexion à Kafka échouée: {e}")
                if retries < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
        raise Exception("Impossible de se connecter à Kafka après plusieurs tentatives")

    def stream_data(self, url: str) -> Iterator[Dict[str, Any]]:
        """Stream des données depuis l'API avec retry"""
        while True:
            try:
                with requests.get(url, stream=True) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            yield data
            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur de connexion à l'API: {e}")
                time.sleep(RETRY_DELAY)
            except json.JSONDecodeError as e:
                logger.error(f"Erreur de décodage JSON: {e}")
                continue

    def send_to_kafka(self, data: list, partition: int = 0):
        """Envoi des données à Kafka avec retry"""
        retries = 0
        while retries < MAX_RETRIES:
            try:
                key = "latest_data"
                self.producer.send(
                    topic=self.topic,
                    key=key,
                    value=data,
                    partition=partition
                )
                self.producer.flush()
                logger.info(f"Données envoyées à Kafka - Topic: {self.topic}, Taille: {len(data)}")
                break
            except Exception as e:
                retries += 1
                logger.error(f"Tentative {retries}/{MAX_RETRIES} d'envoi échouée: {e}")
                if retries < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)

    def run(self):
        logger.info("Démarrage du producteur...")
        try:
            for batch in self.stream_data(API_URL):
                self.send_to_kafka(batch)
        except KeyboardInterrupt:
            logger.info("Arrêt du producteur...")
        finally:
            self.producer.close()

def main():
    while True:
        try:
            producer = StreamProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                topic=KAFKA_TOPIC
            )
            producer.run()
        except Exception as e:
            logger.error(f"Erreur critique: {e}")
            logger.info("Redémarrage du producteur dans 5 secondes...")
            time.sleep(RETRY_DELAY)

if __name__ == "__main__":
    main()