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
```bash
git clone https://github.com/zakaria-333/ml-pipeline-spark-kafka.git
cd ml-pipeline-spark-kafka
