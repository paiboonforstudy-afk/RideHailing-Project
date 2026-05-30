from pyspark import pipelines as dp
from pyspark.sql.functions import col, hour, count, sum, avg

# ── Dim Booker ───────────────────────────────────────────────────────────────
@dp.view
def dim_booker_view():
    return (
        spark.readStream
        .option("skipChangeCommits", "true")
        .option("ignoreDeletes", "true")
        .table("ridehailing.silver.silver_obt")
        .select("booker_id", "booker_name", "booker_email", "booker_phone", "booking_timestamp")
        .dropDuplicates(["booker_id"])
    )

dp.create_streaming_table("dim_booker")
dp.create_auto_cdc_flow(
    target             = "dim_booker",
    source             = "dim_booker_view",
    keys               = ["booker_id"],
    sequence_by        = "booking_timestamp",
    stored_as_scd_type = 1,
)

# ── Dim Driver ────────────────────────────────────────────────────────────────
@dp.view
def dim_driver_view():
    return (
        spark.readStream
        .option("skipChangeCommits", "true")
        .option("ignoreDeletes", "true")
        .table("ridehailing.silver.silver_obt")
        .select("driver_id", "driver_name", "driver_phone", "driver_license", "driver_rating", "booking_timestamp")
        .dropDuplicates(["driver_id"])
    )

dp.create_streaming_table("dim_driver")
dp.create_auto_cdc_flow(
    target             = "dim_driver",
    source             = "dim_driver_view",
    keys               = ["driver_id"],
    sequence_by        = "booking_timestamp",
    stored_as_scd_type = 1,
)

# ── Dim Vehicle ───────────────────────────────────────────────────────────────
@dp.view
def dim_vehicle_view():
    return (
        spark.readStream
        .option("skipChangeCommits", "true")
        .option("ignoreDeletes", "true")
        .table("ridehailing.silver.silver_obt")
        .select("vehicle_id", "vehicle_license_plate", "booking_timestamp")
        .dropDuplicates(["vehicle_id"])
    )

dp.create_streaming_table("dim_vehicle")
dp.create_auto_cdc_flow(
    target             = "dim_vehicle",
    source             = "dim_vehicle_view",
    keys               = ["vehicle_id"],
    sequence_by        = "booking_timestamp",
    stored_as_scd_type = 1,
)

# ── Dim Location (static) ─────────────────────────────────────────────────────
@dp.table
def dim_location():
    return spark.read.table("ridehailing.bronze.map_provinces")

# ── Dim Ride Status (static) ──────────────────────────────────────────────────
@dp.table
def dim_ride_status():
    return spark.read.table("ridehailing.bronze.map_ride_statuses")

# ── Dim Cancellation Reason (static) ─────────────────────────────────────────
@dp.table
def dim_cancellation_reason():
    return spark.read.table("ridehailing.bronze.map_cancellation_reasons")

# ── Dim Ride Option (SCD Type 2) ──────────────────────────────────────────────
@dp.view
def dim_ride_option_view():
    return (
        spark.readStream.table("ridehailing.bronze.map_ride_options")
        .dropDuplicates(["ride_option_id", "loaded_at"])
    )

dp.create_streaming_table("dim_ride_option")
dp.create_auto_cdc_flow(
    target             = "dim_ride_option",
    source             = "dim_ride_option_view",
    keys               = ["ride_option_id"],
    sequence_by        = "loaded_at",
    stored_as_scd_type = 2,
)

# ── Dim Payment (SCD Type 2) ──────────────────────────────────────────────────
@dp.view
def dim_payment_view():
    return (
        spark.readStream.table("ridehailing.bronze.map_payment_methods")
        .dropDuplicates(["payment_method_id", "loaded_at"])
    )

dp.create_streaming_table("dim_payment")
dp.create_auto_cdc_flow(
    target             = "dim_payment",
    source             = "dim_payment_view",
    keys               = ["payment_method_id"],
    sequence_by        = "loaded_at",
    stored_as_scd_type = 2,
)

# ── Fact Rides ────────────────────────────────────────────────────────────────
@dp.view
def fact_rides_view():
    return (
        spark.readStream
        .option("skipChangeCommits", "true")
        .option("ignoreDeletes", "true")
        .table("ridehailing.silver.silver_obt")
        .select(
            "ride_id", "booker_id", "driver_id", "vehicle_id",
            "pickup_city_id", "dropoff_city_id",
            "ride_option_id", "payment_method_id",
            "ride_status_id", "cancellation_reason_id",
            "booking_timestamp", "pickup_timestamp", "dropoff_timestamp",
            "pickup_latitude", "pickup_longitude",
            "dropoff_latitude", "dropoff_longitude",
            "travel_distance_km", "duration_minutes", "passenger_count",
            "base_fare", "distance_fare", "time_fare",
            "surge_multiplier", "subtotal", "tip_amount", "total_fare",
            "driver_rating", "rating",
        )
        .withColumn("booking_date", col("booking_timestamp").cast("date"))
        .withColumn("booking_hour", hour(col("booking_timestamp")))
    )

dp.create_streaming_table("fact_rides")
dp.create_auto_cdc_flow(
    target             = "fact_rides",
    source             = "fact_rides_view",
    keys               = ["ride_id"],
    sequence_by        = "booking_timestamp",
    stored_as_scd_type = 1,
)

# ── Agg Daily (materialized view) ─────────────────────────────────────────────
@dp.table
def agg_daily():
    fact        = spark.read.table("ridehailing.gold.fact_rides")
    ride_status = spark.read.table("ridehailing.gold.dim_ride_status") \
                       .select("ride_status_id", "ride_status")

    return (
        fact
        .join(ride_status, "ride_status_id", "left")
        .withColumn("booking_date", col("booking_date"))
        .groupBy("booking_date")
        .agg(
            count("ride_id")                                      .alias("total_rides"),
            sum("total_fare")                                     .alias("total_revenue"),
            avg("total_fare")                                     .alias("avg_fare"),
            avg("travel_distance_km")                             .alias("avg_distance_km"),
            avg("duration_minutes")                               .alias("avg_duration_min"),
            sum((col("ride_status") == "Completed").cast("int"))  .alias("completed_rides"),
            sum((col("ride_status") == "Cancelled").cast("int"))  .alias("cancelled_rides"),
        )
        .orderBy("booking_date")
    )