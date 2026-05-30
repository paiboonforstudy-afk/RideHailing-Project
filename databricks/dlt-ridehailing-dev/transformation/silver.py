from pyspark import pipelines as dp
from pyspark.sql.functions import *
from pyspark.sql.types import *

rides_schema = StructType([
    StructField("ride_id",                StringType(),  True),
    StructField("booker_id",              StringType(),  True),
    StructField("driver_id",              StringType(),  True),
    StructField("vehicle_id",             StringType(),  True),
    StructField("ride_status_id",         IntegerType(), True),
    StructField('pickup_city_id',  StringType(),  True),
    StructField('dropoff_city_id', StringType(),  True),
    StructField("ride_option_id",         IntegerType(), True),
    StructField("payment_method_id",      IntegerType(), True),
    StructField("booking_timestamp",      StringType(),  True),
    StructField("pickup_latitude",        DoubleType(),  True),
    StructField("pickup_longitude",       DoubleType(),  True),
    StructField("pickup_address",         StringType(),  True),
    StructField("dropoff_latitude",       DoubleType(),  True),
    StructField("dropoff_longitude",      DoubleType(),  True),
    StructField("dropoff_address",        StringType(),  True),
    StructField("booker_name",            StringType(),  True),
    StructField("booker_email",           StringType(),  True),
    StructField("booker_phone",           StringType(),  True),
    StructField("driver_name",            StringType(),  True),
    StructField("driver_phone",           StringType(),  True),
    StructField("driver_license",         StringType(),  True),
    StructField("vehicle_license_plate",  StringType(),  True),
    StructField("cancellation_reason_id", IntegerType(), True),
    StructField("travel_distance_km",     DoubleType(),  True),
    StructField("duration_minutes",       IntegerType(), True),
    StructField("passenger_count",        IntegerType(), True),
    StructField("pickup_timestamp",       StringType(),  True),
    StructField("dropoff_timestamp",      StringType(),  True),
    StructField("driver_rating",          DoubleType(),  True),
    StructField("rating",                 IntegerType(), True),
    StructField("base_fare",              DoubleType(),  True),
    StructField("distance_fare",          DoubleType(),  True),
    StructField("time_fare",              DoubleType(),  True),
    StructField("surge_multiplier",       DoubleType(),  True),
    StructField("subtotal",               DoubleType(),  True),
    StructField("tip_amount",             DoubleType(),  True),
    StructField("total_fare",             DoubleType(),  True),
])

dp.create_streaming_table(
    "stg_rides",
    expect_all_or_drop={
        "valid_ride_id"     : "ride_id IS NOT NULL",
        "valid_total_fare"  : "total_fare >= 0",
        "valid_ride_status" : "ride_status_id IN (1, 2)",
    }
)

@dp.append_flow(target="stg_rides")
def rides_stream():
    df = spark.readStream.table("rides_raw")
    df_parsed = df.withColumn("parsed_rides", from_json(col("rides"), rides_schema)) \
                  .select("parsed_rides.*")
    return df_parsed.withColumn("_source", lit("eventhub"))

@dp.append_flow(target="stg_rides")
def historical_flow():
    return (
        spark.readStream
        .option("skipChangeCommits", "true")
        .table("ridehailing.bronze.bulk_rides")
        .withColumn("_source", lit("historical"))
    )