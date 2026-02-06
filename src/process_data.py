from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, to_timestamp, current_timestamp
import os


def run_spark_job():
    mongo_spark_version = "10.4.0"
    postgres_driver_version = "42.6.0"

    packages = [
        f"org.mongodb.spark:mongo-spark-connector_2.12:{mongo_spark_version}",
        f"org.postgresql:postgresql:{postgres_driver_version}"
    ]

    # Fetch configuration from Environment Variables
    mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:password@mongo:27017")
    mongo_db = os.getenv("MONGO_DB_NAME", "rte")
    mongo_collection = os.getenv("MONGO_COLLECTION", "eco2mix_regional_tr")

    postgres_user = os.getenv("DB_USER", "airflow")
    postgres_password = os.getenv("DB_PASSWORD", "airflow")
    postgres_host = os.getenv("DB_HOST", "postgres")
    postgres_port = os.getenv("DB_PORT", "5432")
    data_db_name = os.getenv("DATA_DB_NAME", "rte_data")

    full_mongo_uri = f"{mongo_uri}/{mongo_db}.{mongo_collection}?authSource=admin"

    spark = SparkSession.builder \
        .appName("RTE Data Processing") \
        .config("spark.jars.packages", ",".join(packages)) \
        .config("spark.mongodb.read.connection.uri", full_mongo_uri) \
        .config("spark.mongodb.write.connection.uri", full_mongo_uri) \
        .getOrCreate()

    df = spark.read.format("mongodb").load()

    print("Schema from MongoDB:")
    df.printSchema()

    # Transformation:
    # 1. Cast numeric columns
    # 2. Group by Region, Nature AND Date/Time (to keep history)
    # 3. Add processing timestamp

    df_processed = df.withColumn("consommation", col("consommation").cast("int")) \
                     .withColumn("ech_physiques", col("ech_physiques").cast("int")) \
                     .withColumn("date_heure", to_timestamp(col("date_heure")))

    agg_df = df_processed.groupBy("libelle_region", "nature", "date_heure") \
        .agg(
            avg("consommation").alias("avg_consumption"),
            avg("ech_physiques").alias("avg_physical_exchange"),
            count("*").alias("record_count")
        ) \
        .withColumn("processed_at", current_timestamp())

    print("Aggregated Data Preview:")
    agg_df.show()

    jdbc_url = f"jdbc:postgresql://{postgres_host}:{postgres_port}/{data_db_name}"
    properties = {
        "user": postgres_user,
        "password": postgres_password,
        "driver": "org.postgresql.Driver"
    }

    agg_df.write.jdbc(url=jdbc_url, table="regional_energy_stats", mode="append", properties=properties)

    print("Data successfully written to PostgreSQL")
    spark.stop()


if __name__ == "__main__":
    run_spark_job()
