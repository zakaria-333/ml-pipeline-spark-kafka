# Pipeline de Machine Learning avec Architecture Kappa

## Table des Matières
1. [Description du Projet](#description-du-projet)
2. [Architecture du Projet](#architecture-du-projet)
3. [Guide d'Installation](#guide-dinstallation)
   - [3.1 Pré-requis](#31-pré-requis)
   - [3.2 Clonage du Projet](#32-clonage-du-projet)
   - [3.3 Démarrage des Conteneurs](#33-démarrage-des-conteneurs)
   - [3.4 Configuration de Spark-Master](#34-configuration-de-spark-master)
4. [Lancement du Pipeline](#lancement-du-pipeline)
   - [4.1 Kafka-UI](#41-kafka-ui)
   - [4.2 Consommateur Spark](#42-consommateur-spark)
   - [4.3 Producteur Kafka](#43-producteur-kafka)
   - [4.4 Visualisation de la Variation de RMSE](#44-visualisation-de-la-variation-de-rmse)
   - [4.5 Prédictions](#45-prédictions)

---

## 1. Description du Projet
Ce projet implémente un pipeline de machine learning en temps réel basé sur l'architecture Kappa. Il permet de traiter et d’analyser des données d’émissions de CO2 pour effectuer des prédictions dynamiques. Les données sont diffusées via une API FastAPI, ingérées dans Kafka, traitées par Apache Spark, et visualisées grâce à Streamlit.

---

## 2. Architecture du Projet
![kappa_online_ml](https://github.com/user-attachments/assets/4523dd2b-a882-4e1e-9da2-82d23dfa70d4)

Le projet suit l'architecture Kappa, composée des éléments suivants :
- **FastAPI** : Fournit une API pour diffuser les données du fichier CSV.
- **Kafka** : Sert de middleware pour transmettre les données en temps réel.
- **Spark** : Consomme les flux de Kafka et applique des modèles de machine learning.
- **Streamlit** : Visualise les prédictions et les métriques du modèle en temps réel.

---

## 3. Guide d'Installation

### 3.1 Pré-requis
- Docker Desktop installé sur votre système (vérifiez avec `docker --version`).

### 3.2 Clonage du Projet
Clonez le dépôt Git avec la commande suivante :
```
git clone https://github.com/zakaria-333/ml-pipeline-spark-kafka.git
cd ml-pipeline-spark-kafka
```
### 3.3 Démarrage des Conteneurs
Accédez au dossier api :
```
cd api
docker build -t streaming-api .
```
Revenez au répertoire racine :
```
cd ..
docker-compose up -d
```
Docker Compose lance tous les conteneurs nécessaires (Kafka, Zookeeper, Spark, API).

### 3.4 Configuration de Spark-Master
Accédez au conteneur Spark-Master :
```
docker exec -it spark-master bash
```
Naviguez dans le répertoire /app et installez les dépendances :
```
cd /app
pip install scikit-learn kafka-python streamlit
```
## 4. Lancement du Pipeline
### 4.1 Kafka-UI
Accédez à l'interface Kafka à l'adresse :
http://localhost:8080
Ajoutez un topic nommé streaming_data.

### 4.2 Consommateur Spark
Le consommateur traite les données envoyées par Kafka. Exécutez la commande suivante dans un terminal Spark-Master :
```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2 --jars kafka-clients-3.8.0.jar --driver-class-path kafka-clients-3.8.0.jar kafka_consumer.py
```
### 4.3 Producteur Kafka
Le producteur lit les données du fichier CSV et les publie sur le topic Kafka. Lancez-le dans un autre terminal Spark-Master :
```
spark-submit kafka_producer.py
```
### 4.4 Visualisation de la Variation de RMSE
Démarrez l'interface d'évaluation Streamlit pour suivre les performances du modèle :
```
python -m streamlit run streamlit-eval.py
```
Accédez à l’interface via l'URL fournie.

### 4.5 Prédictions
Pour visualiser les prédictions des émissions de CO2, lancez l'interface :
```
python -m streamlit run streamlit-prediction.py
```
---
## Remarques
- Consommateur avant Producteur : Lancez le consommateur Spark avant le producteur Kafka pour garantir un traitement fluide des données.
- Utilisation de plusieurs terminaux : Chaque commande Spark doit être exécutée dans un terminal Spark-Master distinct.
