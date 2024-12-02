import os
import pyspark
from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegression, LinearRegressionModel
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.functions import col, from_json, explode
from pyspark.sql.types import StructType, StructField, DoubleType, BooleanType, ArrayType

# Kafka Topic Configuration
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "streaming_data"  # Updated to match your producer's topic

# Spark Session
spark = SparkSession.builder \
    .appName("VehicleFuelConsumptionRegression") \
    .getOrCreate()

# Kafka Schema (based on your data structure)
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

# Model Path
MODEL_PATH = "./spark_vehicle_model"

# Load or Initialize Model
if os.path.exists(MODEL_PATH):
    print("Loading existing model...")
    model = LinearRegressionModel.load(MODEL_PATH)
else:
    print("No existing model found. Initializing new model...")
    model = None

# Kafka Stream DataFrame
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

# Parse Kafka value as JSON and explode the array
data = df.select(from_json(col("value").cast("string"), ArrayType(schema)).alias("data")) \
    .select(explode(col("data")).alias("record"))

# Prepare Data for Training
# Choose features for prediction (you can adjust these)
feature_cols = [
    "Engine_Size", 
    "Cylinders", 
    "Fuel_Consumption_City", 
    "Fuel_Consumption_Hwy"
]

# Target variable (you can change this based on your prediction goal)
target_col = "CO2_Emissions"

# Vector Assembler
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

# Clean the data (filter out rows with null values in the features)
clean_data = data.select("record.*").filter(
    col("Engine_Size").isNotNull() & 
    col("Cylinders").isNotNull() & 
    col("Fuel_Consumption_City").isNotNull() & 
    col("Fuel_Consumption_Hwy").isNotNull()
)

# Transform data into feature vector
train_data = assembler.transform(clean_data).select("features", col(target_col).alias("label"))

def incremental_train(batch_df, batch_id):
    global model
    if batch_df.isEmpty():
        print("Batch is empty, skipping this batch.")
        return
    
    # Display batch data for verification
    batch_df.show(5, truncate=False)
   
    if model is None:
        print("Training initial model...")
        lr = LinearRegression(featuresCol="features", labelCol="label", maxIter=10)
        model = lr.fit(batch_df)
    else:
        print("Training incremental model...")
        # Apply existing model to current batch
        transformed_batch = model.transform(batch_df)
        
        # Select necessary columns before union
        transformed_batch = transformed_batch.select("features", "label")
       
        # Retrain the model with combined data
        combined_data = transformed_batch.union(batch_df)
        lr = LinearRegression(featuresCol="features", labelCol="label", maxIter=10)
        model = lr.fit(combined_data)
   
    # Save the updated model
    model.write().overwrite().save(MODEL_PATH)
    print(f"Model updated and saved.")
    print(f"Coefficients: {model.coefficients}")
    print(f"Intercept: {model.intercept}")

# Stream Query
query = train_data.writeStream \
    .foreachBatch(incremental_train) \
    .outputMode("update") \
    .start()

query.awaitTermination()