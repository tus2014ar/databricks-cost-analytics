# Databricks notebook source
# MAGIC %md
# MAGIC # 4.0 Spend Forecast — Databricks Cost Analytics
# MAGIC
# MAGIC Fits a trailing-90-day linear regression to daily spend — account-wide and for the
# MAGIC top cost objects — and projects an annualized spend range from it.
# MAGIC
# MAGIC **Source:** `gold_daily_spend_trend` (account-wide), `gold_top_cost_objects_current`
# MAGIC joined back to `gold_fact_usage` (per-object daily series).
# MAGIC **Target:** `gold_spend_forecast` — one row per forecast scope (`ACCOUNT` or an
# MAGIC individual `object_sk`), rebuilt in full on every run (`INSERT OVERWRITE`).
# MAGIC
# MAGIC **Method:** ordinary least squares on `daily_cost` vs. day-index over the trailing
# MAGIC window (default 90 days, configurable via widget). The fitted line's value at the most
# MAGIC recent day is annualized (`× 365`) for the midpoint; the regression's residual standard
# MAGIC error gives a ±1 std-dev band around it. Objects with fewer than `min_days_history` days
# MAGIC of billing activity in the window are skipped — a trend fit on a handful of points isn't
# MAGIC a trend, it's noise.

# COMMAND ----------

# DBTITLE 1,imports
# MAGIC %run ./init_libraries

# COMMAND ----------

import numpy as np

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 3 - Widgets

# COMMAND ----------

dbutils.widgets.text("environment",       "dev")
dbutils.widgets.text("verbose",           "False")
dbutils.widgets.text("trailing_days",     "90")
dbutils.widgets.text("min_days_history",  "14")
dbutils.widgets.text("top_n_objects",     "20")

environment      = dbutils.widgets.get("environment").strip().lower()
verbose          = dbutils.widgets.get("verbose").strip().lower() == "true"
trailing_days    = int(dbutils.widgets.get("trailing_days"))
min_days_history = int(dbutils.widgets.get("min_days_history"))
top_n_objects    = int(dbutils.widgets.get("top_n_objects"))
prefix           = "dev_" if environment == "dev" else ""

CATALOG = "data_automation"
SCHEMA  = "databricks_analytics"

target_catalog = f"{prefix}{CATALOG}"

print(f"  environment       = {environment}")
print(f"  trailing_days     = {trailing_days}")
print(f"  min_days_history  = {min_days_history}")
print(f"  top_n_objects     = {top_n_objects}")
print(f"  target catalog    = {target_catalog}")
print(f"  target schema     = {SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 4 - Guard

# COMMAND ----------

assert environment in ("dev", "prod"), f"Invalid environment: '{environment}'. Must be 'dev' or 'prod'."
assert trailing_days >= min_days_history, "trailing_days must be >= min_days_history."

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 5 - Regression helper

# COMMAND ----------

# DBTITLE 1,fit_trend
def fit_trend(daily_costs: np.ndarray) -> dict:
    """
    Fit an OLS line (degree-1 polyfit) to a daily cost series and project it forward.

    `daily_costs` is ordered oldest -> newest. Returns the fitted rate at the most
    recent day, the annualized midpoint/low/high band (+/- 1 residual std dev,
    floored at 0 since spend can't go negative), and the fitted slope so the sign
    of the trend (accelerating vs. flat vs. declining) is queryable downstream.
    """
    n = len(daily_costs)
    day_index = np.arange(n)

    slope, intercept = np.polyfit(day_index, daily_costs, deg=1)
    fitted = slope * day_index + intercept
    residual_std = float(np.std(daily_costs - fitted))

    latest_fitted_rate = float(slope * (n - 1) + intercept)
    annual_mid = latest_fitted_rate * 365
    annual_band = residual_std * 365

    return {
        "n_days_used": n,
        "daily_rate_fitted": latest_fitted_rate,
        "trend_slope_daily": float(slope),
        "residual_std_daily": residual_std,
        "projected_annual_low": max(0.0, annual_mid - annual_band),
        "projected_annual_mid": max(0.0, annual_mid),
        "projected_annual_high": max(0.0, annual_mid + annual_band),
    }

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 6 - Account-wide forecast

# COMMAND ----------

# DBTITLE 1,account_forecast
account_trend_df = spark.sql(f"""
    SELECT usage_date, daily_cost
    FROM {target_catalog}.{SCHEMA}.gold_daily_spend_trend
    ORDER BY usage_date DESC
    LIMIT {trailing_days}
""").toPandas().sort_values("usage_date")

account_rows = []
if len(account_trend_df) >= min_days_history:
    fit = fit_trend(account_trend_df["daily_cost"].to_numpy(dtype=float))
    account_rows.append({
        "scope": "ACCOUNT",
        "object_sk": None,
        "object_identifier": None,
        **fit,
    })
    if verbose:
        print(f"ACCOUNT: fitted daily rate ${fit['daily_rate_fitted']:.2f}, "
              f"projected annual ${fit['projected_annual_low']:.0f}-${fit['projected_annual_high']:.0f}")
else:
    print(f"WARNING: only {len(account_trend_df)} days of account-wide history "
          f"(< min_days_history={min_days_history}) — skipping account forecast.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 7 - Per-object forecast (top N by lifetime cost)

# COMMAND ----------

# DBTITLE 1,object_forecast
top_objects = spark.sql(f"""
    SELECT object_sk, object_identifier
    FROM {target_catalog}.{SCHEMA}.gold_top_cost_objects_current
    WHERE deleted_indicator = FALSE
    ORDER BY cost_rank
    LIMIT {top_n_objects}
""").collect()

object_daily_df = spark.sql(f"""
    SELECT
        object_sk,
        usage_date,
        SUM(total_cost) AS daily_cost
    FROM {target_catalog}.{SCHEMA}.gold_fact_usage
    WHERE usage_date >= date_sub(current_date(), {trailing_days})
      AND object_sk IN ({",".join(str(r["object_sk"]) for r in top_objects) or "-1"})
    GROUP BY object_sk, usage_date
""").toPandas()

object_rows = []
skipped = 0
for row in top_objects:
    obj_series = (
        object_daily_df[object_daily_df["object_sk"] == row["object_sk"]]
        .sort_values("usage_date")["daily_cost"]
        .to_numpy(dtype=float)
    )
    if len(obj_series) < min_days_history:
        skipped += 1
        continue
    fit = fit_trend(obj_series)
    object_rows.append({
        "scope": "OBJECT",
        "object_sk": row["object_sk"],
        "object_identifier": row["object_identifier"],
        **fit,
    })

print(f"Forecasted {len(object_rows)} of {len(top_objects)} top objects "
      f"({skipped} skipped: fewer than {min_days_history} days of activity in the window).")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 8 - Write gold_spend_forecast

# COMMAND ----------

# DBTITLE 1,gold_spend_forecast - write
all_rows = account_rows + object_rows

# Schema for the rows produced by fit_trend() — forecast_sk/method/forecast_run_date
# are derived afterward, so they're not part of the input schema.
computed_schema = T.StructType([
    T.StructField("scope",                  T.StringType(), False),
    T.StructField("object_sk",              T.LongType(),   True),
    T.StructField("object_identifier",      T.StringType(), True),
    T.StructField("n_days_used",            T.IntegerType(),False),
    T.StructField("daily_rate_fitted",      T.DoubleType(), False),
    T.StructField("trend_slope_daily",      T.DoubleType(), False),
    T.StructField("residual_std_daily",     T.DoubleType(), False),
    T.StructField("projected_annual_low",   T.DoubleType(), False),
    T.StructField("projected_annual_mid",   T.DoubleType(), False),
    T.StructField("projected_annual_high",  T.DoubleType(), False),
])

# Full target column order for gold_spend_forecast, including the derived columns.
FORECAST_COLUMNS = [
    "forecast_sk", "scope", "object_sk", "object_identifier", "n_days_used",
    "daily_rate_fitted", "trend_slope_daily", "residual_std_daily",
    "projected_annual_low", "projected_annual_mid", "projected_annual_high",
    "method", "forecast_run_date",
]

if all_rows:
    forecast_df = spark.createDataFrame(all_rows, schema=computed_schema) \
        .withColumn("method", F.lit(f"ols_trailing_{trailing_days}d")) \
        .withColumn("forecast_run_date", F.current_date()) \
        .withColumn(
            "forecast_sk",
            F.xxhash64(
                F.coalesce(F.col("scope"), F.lit("")),
                F.coalesce(F.col("object_sk").cast("string"), F.lit("ACCOUNT")),
                F.col("forecast_run_date").cast("string"),
            ),
        ) \
        .select(FORECAST_COLUMNS)

    forecast_df.write.mode("overwrite").saveAsTable(f"{target_catalog}.{SCHEMA}.gold_spend_forecast")

    print(f"Wrote {forecast_df.count()} row(s) to {target_catalog}.{SCHEMA}.gold_spend_forecast")
    if verbose:
        display(forecast_df.orderBy(F.col("projected_annual_mid").desc()))
else:
    print("No rows to forecast — check upstream tables have data.")
