from pyspark import pipelines as dp
from pyspark.sql.functions import col

@dp.table
def silver_obt():
    rides = (
        spark.readStream
        .option("ignoreDeletes", "true")
        .table("ridehailing.bronze.stg_rides")
    )

    map_ride_options    = spark.read.table("ridehailing.bronze.map_ride_options") \
                               .select("ride_option_id", "ride_option_name", "vehicle_class")
    map_payment_methods = spark.read.table("ridehailing.bronze.map_payment_methods") \
                               .select("payment_method_id", "payment_method")
    map_ride_statuses   = spark.read.table("ridehailing.bronze.map_ride_statuses") \
                               .select("ride_status_id", "ride_status")
    map_cancellation    = spark.read.table("ridehailing.bronze.map_cancellation_reasons") \
                               .select("cancellation_reason_id", "initiator", "cancellation_reason")
    map_pickup          = spark.read.table("ridehailing.bronze.map_provinces") \
                               .select(
                                   col("province_id").alias("pickup_city_id"),
                                   col("province_name").alias("pickup_province")
                               )
    map_dropoff         = spark.read.table("ridehailing.bronze.map_provinces") \
                               .select(
                                   col("province_id").alias("dropoff_city_id"),
                                   col("province_name").alias("dropoff_province")
                               )

    return (
        rides
        .join(map_ride_options,    "ride_option_id",         "left")
        .join(map_payment_methods, "payment_method_id",      "left")
        .join(map_ride_statuses,   "ride_status_id",         "left")
        .join(map_cancellation,    "cancellation_reason_id", "left")
        .join(map_pickup,          "pickup_city_id",         "left")
        .join(map_dropoff,         "dropoff_city_id",        "left")
        .withColumn("booking_timestamp", col("booking_timestamp").cast("timestamp"))
        .withColumn("pickup_timestamp",  col("pickup_timestamp").cast("timestamp"))
        .withColumn("dropoff_timestamp", col("dropoff_timestamp").cast("timestamp"))
    )