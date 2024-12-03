import os
import numpy as np
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.functions import col, from_json, explode
from pyspark.sql.types import StructType, StructField, DoubleType, BooleanType, ArrayType
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import root_mean_squared_error
import joblib
import json

# Configuration
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "streaming_data"  # Topic Kafka utilisé
MODEL_PATH = "./sgd.joblib"  # Chemin pour sauvegarder le modèle
METRICS_PATH = "./metric1.json"  # Chemin pour sauvegarder les métriques RMSE

# Initialiser la session Spark
spark = SparkSession.builder \
    .appName("VehicleFuelConsumptionRegression") \
    .getOrCreate()

# Définir le schéma des données Kafka
schema = StructType([
    StructField("Engine_Size", DoubleType(), True),
    StructField("Cylinders", DoubleType(), True),
    StructField("Fuel_Consumption_City", DoubleType(), True),
    StructField("Fuel_Consumption_Hwy", DoubleType(), True),
    StructField("Fuel_Consumption_Comb", DoubleType(), True),
    StructField("CO2_Emissions", DoubleType(), True),
    StructField("Fuel_Type_D", BooleanType(), True),
    StructField("Fuel_Type_E", BooleanType(), True),
    StructField("Fuel_Type_N", BooleanType(), True),
    StructField("Fuel_Type_X", BooleanType(), True),
    StructField("Fuel_Type_Z", BooleanType(), True)
])

# Charger ou initialiser le modèle
if os.path.exists(MODEL_PATH):
    print("Loading existing model...")
    model = joblib.load(MODEL_PATH)
else:
    print("No existing model found. Initializing new model...")
    model = SGDRegressor(max_iter=1000, tol=1e-3)

# Charger les métriques
if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH, "r") as f:
        metrics = json.load(f)
else:
    metrics = {"batch": [], "rmse": []}

# Lire les données du flux Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

data = df.select(from_json(col("value").cast("string"), ArrayType(schema)).alias("data")) \
    .select(explode(col("data")).alias("record"))

feature_cols = [
    "Engine_Size", "Cylinders", "Fuel_Consumption_City", 
    "Fuel_Consumption_Hwy", "Fuel_Consumption_Comb", 
    "Fuel_Type_D", "Fuel_Type_E", "Fuel_Type_N", 
    "Fuel_Type_X", "Fuel_Type_Z"
]
target_col = "CO2_Emissions"

assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

clean_data = data.select("record.*").filter(
    col("Engine_Size").isNotNull() &
    col("Cylinders").isNotNull() &
    col("Fuel_Consumption_City").isNotNull() &
    col("Fuel_Consumption_Hwy").isNotNull() &
    col("Fuel_Consumption_Comb").isNotNull() &
    col("Fuel_Type_D").isNotNull() &
    col("Fuel_Type_E").isNotNull() &
    col("Fuel_Type_N").isNotNull() &
    col("Fuel_Type_X").isNotNull() &
    col("Fuel_Type_Z").isNotNull()
)

train_data = assembler.transform(clean_data).select("features", col(target_col).alias("label"))

def incremental_train(batch_df, batch_id):
    global model
    if batch_df.isEmpty():
        print("Batch is empty, skipping this batch.")
        return

    # Convertir les données en arrays pour scikit-learn
    features = np.array(batch_df.select("features").rdd.map(lambda row: row[0].toArray()).collect())
    labels = np.array(batch_df.select("label").rdd.map(lambda row: row[0]).collect())

    # Si modèle inexistant, initialiser
    if model is None:
        model = SGDRegressor(max_iter=1000, tol=1e-3)
        model.fit(features, labels)
    else:
        model.partial_fit(features, labels)

    # Calculer le RMSE pour le batch courant
   
    predictions = model.predict(features)
    rmse = root_mean_squared_error(labels, predictions)

    # Mettre à jour les métriques
    metrics["batch"].append(batch_id)
    metrics["rmse"].append(rmse)

    # Sauvegarder les métriques
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f)

    # Sauvegarder le modèle
    joblib.dump(model, MODEL_PATH)
    print(f"Batch {batch_id}: RMSE = {rmse:.4f}")

query = train_data.writeStream \
    .foreachBatch(incremental_train) \
    .outputMode("update") \
    .start()

query.awaitTermination()