# Load Pattern Decisions

**Pipeline:** Databricks Cost Analytics  
**Domain:** data_automation  
**Schema:** databricks_analytics  
**Author:** Tushar — Data + Automation Team  
**Date:** May 2026  
**Status:** In-review

---

## Overview

This document defines the load pattern decision for every silver and gold table
in the Databricks Cost Analytics pipeline. Decisions are made by applying the
Load Pattern Decision Guide from the Databricks SQL Load Patterns Reference
(Process Standards) against source system characteristics confirmed during EDA
and system table profiling.

All silver tables read directly from Databricks system tables.  
All gold tables read from silver — never from bronze directly, per the Silver + Gold Modeling Reference standard.

The `environment` parameter controls catalog targeting at runtime. All table
references in notebooks use `IDENTIFIER(:prefix || '...')`.

```
Dev:  dev_data_automation.databricks_analytics.<table>
Prod: data_automation.databricks_analytics.<table>
```

---

## Silver Tables

| Table                          | Load Pattern                                   | Trigger | Partition        | Key Decision                                                                                        |
| ------------------------------ | ---------------------------------------------- | ------- | ---------------- | --------------------------------------------------------------------------------------------------- |
| `silver_usage_history`         | Append with Watermark                          | Daily   | `usage_hour`     | Records immutable — EDA: 0 duplicates, `record_id` unique across 268,127 rows                       |
| `silver_list_prices_history`   | Full Overwrite                                 | Daily   | None             | ~100 rows; full rebuild cost negligible                                                             |
| `silver_cluster_current`       | Full Overwrite with ROW_NUMBER() Deduplication | Daily   | None             | 1,000 rows / 492 distinct IDs — `change_time` only reliable timestamp; `last_restarted_time` absent |
| `silver_warehouse_current`     | Full Overwrite with ROW_NUMBER() Deduplication | Daily   | None             | 30 rows / 18 distinct IDs — `change_time` only reliable timestamp; 12 with duplicate versions       |
| `silver_job_current`           | Full Overwrite with ROW_NUMBER() Deduplication | Daily   | None             | 1,000 rows / 489 distinct IDs — `change_time` only reliable timestamp; no reliable email owner      |
| `silver_workspace_current`     | Full Overwrite                                 | Daily   | None             | `_latest` table — delivers current state only; no stale re-delivery possible                        |
| `silver_pipeline_current`      | Full Overwrite with ROW_NUMBER() Deduplication | Daily   | None             | 1,000 rows / 402 distinct IDs — 85% duplicate rate; `create_time` NULL throughout                   |
| `silver_served_entity_current` | Full Overwrite with ROW_NUMBER() Deduplication | Daily   | None             | Multiple config versions per `served_entity_id` confirmed; `change_time` only reliable timestamp    |
| `silver_query_history`         | Append with Watermark                          | Daily   | `query_start_hour` | Records immutable — `start_timestamp` is watermark column. All statuses retained at silver. Sourced from `system.query.history` |


---

### **1. silver_usage_history — Append with Watermark**

**Source:** `system.billing.usage`  
**PK:** `record_identifier` (natural key, NOT NULL)  
**Grain:** One row per billing usage record — source aggregated by hour. Each row represents up to one hour of compute activity. Runs longer than one hour produce multiple rows, one per clock-hour boundary.  
**Partition:** `usage_hour` (derived as `DATE_TRUNC('HOUR', usage_start_timestamp)`)

**Why Append with Watermark:**  
Billing records are immutable once written. EDA confirmed 0 duplicates and 100% unique `record_id` across the full 268,127-row history. An append pattern is correct — there is nothing to update. Watermark filters to only new rows on each run, avoiding full reprocessing of three years of history.

**Watermark expression:**

sql

```sql
usage_start_timestamp > (
    SELECT COALESCE(
        MAX(usage_start_timestamp),
        CAST('1900-01-01T00:00:00' AS TIMESTAMP)
    )
    FROM silver_usage_history
)
```

The watermark operates at timestamp granularity. If the pipeline fails mid-run, the next run picks up from the exact last successfully loaded timestamp. No row is skipped and no row is duplicated. The COALESCE handles the first run when the table is empty.

Partial hour exclusion is not handled at silver load time. The current in-progress hour is loaded as rows become available from the source. Filtering to completed hours is handled at the dashboarding layer.

**Partition key —** `usage_hour` **derived from** `usage_start_timestamp`**:**

sql

```sql
DATE_TRUNC('HOUR', usage_start_timestamp) AS usage_hour
```

Partitioning on the raw `usage_start_timestamp` TIMESTAMP with millisecond precision would create one partition per distinct timestamp value — breaking Delta metadata performance. Truncating to hour gives one partition per hour of billing activity. Over three years of history that is approximately 26,000 partitions — manageable for Delta and aligned with hourly grain. Full timestamp precision is retained in `usage_start_timestamp` at the row level for exact filtering.

**Documented assumption — correction rows are possible but not observed:**  
EDA confirmed 0 RETRACTION or RESTATEMENT rows across 268,127 rows in the current history. Correction rows are possible per Databricks documentation — when a correction occurs, a RETRACTION row with negative `usage_quantity` is added to negate the original, followed by a RESTATEMENT row with the corrected values. Because corrections are appended as new rows with the original `usage_start_timestamp`, a strict forward-only watermark could miss them if the corrected timestamp falls behind the current watermark position. This risk is accepted and documented. If correction rows are observed in future, this decision must be revisited and a lookback buffer or `record_type` filter added.

**No cost derivation at silver:**  
`silver_usage_history` carries raw `usage_quantity` only. Price data lives in `silver_list_prices_history`. Cost calculation is not performed at silver load time — keeping the two concerns cleanly separated. Hourly and daily cost are derived at the gold view layer:

- `gold_daily_spend_trend` derives cost as `SUM(usage_quantity × pricing.default)` joining `silver_usage_history` to `silver_list_prices_history` at query time
- No join to `silver_list_prices_history` at silver load time

---

### **2. silver_list_prices_history — Full Overwrite**

**Source:** `system.billing.list_prices`  
**PK:** `sku_name + price_start_timestamp` (composite natural key, both NOT NULL)  
**Grain:** One row per SKU per price effective period

**Why Full Overwrite:**  
Prices change over time by SKU and the source delivers the complete price history on every extract. The table is small (~100 rows). Full rebuild cost is negligible and simpler than MERGE for a reference table.

**Purpose of this table in the pipeline:**  
Standalone price reference table. Does not join to `silver_usage_history` at silver load time. The gold view `gold_daily_spend_trend` joins this table to `silver_usage_history` at query time to derive hourly and daily cost using `pricing.default` as the unit price:

sql

```sql
    silver_usage_history.sku_name = silver_list_prices_history.sku_name
AND silver_usage_history.usage_start_timestamp
    BETWEEN silver_list_prices_history.price_start_timestamp
    AND COALESCE(silver_list_prices_history.price_end_timestamp, CURRENT_TIMESTAMP())
```

`pricing.default` is the published standard list price per Databricks documentation and is the officially endorsed field for cost calculation — confirmed from the Databricks sample query: `usage_quantity * list_prices.pricing.default as list_cost`. Promotional rates are not applied. Cost figures represent the full list price throughout. During promotional periods the actual billed amount may be lower. This is a deliberate design decision accepted and documented.

---

### 3. **silver_cluster_current — Full Overwrite with ROW_NUMBER() Deduplication**

**Source:** `system.compute.clusters`  
**PK:** `cluster_identifier` (natural key, NOT NULL — after dedup)  
**Grain:** One row per cluster (current configuration version)

**Why Full Overwrite with ROW_NUMBER() Deduplication:**  
`system.compute.clusters` delivers the full configuration history of every cluster on every extract — multiple rows per `cluster_id`. Live extract confirmed 1,000 rows across only 492 distinct cluster IDs — 399 IDs have multiple configuration versions confirming stale re-delivery. `change_time` is populated for all 1,000 rows and is the only reliable timestamp in this table. Full Overwrite with ROW_NUMBER() Deduplication is correct — deduplicate the full extract to one row per cluster, then overwrite silver completely. No stale row can survive a full rebuild.

**Dedup before overwrite:**

sql

```sql
ROW_NUMBER() OVER (PARTITION BY cluster_id ORDER BY change_time DESC) = 1
```

**Derived column — deleted_indicator:**

sql

```sql
deleted_indicator = CASE WHEN delete_time IS NOT NULL THEN TRUE ELSE FALSE END
```

484 deleted clusters confirmed in live extract. Deleted clusters are retained in silver — never excluded. `deleted_indicator` enables filtering between active and deleted clusters at gold without touching the raw `delete_time` column.

**Live source findings — May 2026:**

- 1,000 total rows — 492 distinct cluster IDs
- 399 cluster IDs have multiple configuration versions
- `change_time` populated for all 1,000 rows — confirmed dedup key
- 484 clusters deleted (`delete_time` populated) — retained, not excluded
- `deleted_indicator` derived as `delete_time IS NOT NULL`
- `owned_by` is the owner field — maps to `owner_email` in silver
- Join hit rate: 99.6%

**FK declared:** `workspace_identifier` → `silver_workspace_current.workspace_identifier`

---

### 4. **silver_warehouse_current — Full Overwrite with ROW_NUMBER() Deduplication**

**Source:** `system.compute.warehouses`  
**PK:** `warehouse_identifier` (natural key, NOT NULL — after dedup)  
**Grain:** One row per SQL warehouse (current configuration version)  
**Partition:** None

**Why Full Overwrite with ROW_NUMBER() Deduplication:**  
`system.compute.warehouses` delivers the full configuration history of every warehouse on every extract — multiple rows per `warehouse_id`. Live extract confirmed 30 rows across only 18 distinct warehouse IDs — 12 have multiple configuration versions confirming stale re-delivery. `change_time` is populated for all 30 rows and is the only reliable timestamp in this table. Full Overwrite with ROW_NUMBER() Deduplication is correct — deduplicate the full extract to one row per warehouse, then overwrite silver completely.

**Dedup before overwrite:**

sql

```sql
ROW_NUMBER() OVER (PARTITION BY warehouse_id ORDER BY change_time DESC) = 1
```

**Derived column — deleted_indicator:**

sql

```sql
deleted_indicator = CASE WHEN delete_time IS NOT NULL THEN TRUE ELSE FALSE END
```

13 deleted warehouses confirmed in live extract. Deleted warehouses are retained in silver — never excluded.

**Live source findings — May 2026:**

- 30 total rows — 18 distinct warehouse IDs
- 12 warehouse IDs have multiple configuration versions
- `change_time` populated for all 30 rows — confirmed dedup key
- 13 warehouses deleted (`delete_time` populated) — retained, not excluded
- `deleted_indicator` derived as `delete_time IS NOT NULL`
- `created_by` is the owner field — maps to `creator_email` in silver
- `warehouse_channel` is a flat column — not a nested struct
- `min_clusters` and `max_clusters` are the actual column names in source
- `enable_photon`, `spot_instance_policy`, `state` columns absent from source

**FK declared:** `workspace_identifier` → `silver_workspace_current.workspace_identifier`

---

### 5. **silver_job_current — Full Overwrite with ROW_NUMBER() Deduplication**

**Source:** `system.lakeflow.jobs`  
**PK:** `job_identifier` (natural key, NOT NULL — after dedup)  
**Grain:** One row per job (current configuration version)  
**Partition:** None

**Why Full Overwrite with ROW_NUMBER() Deduplication:**  
`system.lakeflow.jobs` delivers the full configuration history of every job on every extract — multiple rows per `job_id`. Live extract confirmed 1,000 rows across only 489 distinct job IDs — 140 have multiple configuration versions confirming stale re-delivery. `change_time` is populated for all 1,000 rows and is the only reliable timestamp in this table. Full Overwrite with ROW_NUMBER() Deduplication is correct — deduplicate the full extract to one row per job, then overwrite silver completely.

**Dedup before overwrite:**

sql

```sql
ROW_NUMBER() OVER (PARTITION BY job_id ORDER BY change_time DESC) = 1
```

**Derived column — deleted_indicator:**

sql

```sql
deleted_indicator = CASE WHEN delete_time IS NOT NULL THEN TRUE ELSE FALSE END
```

432 deleted jobs confirmed in live extract. Deleted jobs are retained in silver — never excluded.

**Owner field — no reliable email available:**  
`creator_user_name` is NULL for 941 of 1,000 rows — not usable for attribution. `run_as_user_name` is populated for only 59 rows. `creator_id` and `run_as` are 100% and 99.3% populated respectively but both hold system IDs (`<EXAMPLE_SYSTEM_ID>`) — not human-readable email addresses. Owner resolution for job cost objects will return UNRESOLVED at gold for most rows. This is a known source limitation — documented as an open item.

**Live source findings — May 2026:**

- 1,000 total rows — 489 distinct job IDs
- 140 job IDs have multiple configuration versions
- `change_time` populated for all 1,000 rows — confirmed dedup key
- `create_time` NULL for 941 of 1,000 rows — not usable
- 432 jobs deleted (`delete_time` populated) — retained, not excluded
- `deleted_indicator` derived as `delete_time IS NOT NULL`
- `creator_user_name` NULL for 941 rows — not a reliable owner field
- `run_as_user_name` populated for only 59 rows — not reliable
- `creator_id` and `run_as` 100% populated — system IDs only, not email addresses
- `format` column absent from source — removed from silver DDL
- New columns available: `description`, `trigger_type`, `run_as_user_name`, `paused`

**FK declared:** `workspace_identifier` → `silver_workspace_current.workspace_identifier`

---

### 6. **silver_workspace_current — Full Overwrite**

**Source:** `system.access.workspaces_latest`  
**PK:** `workspace_identifier` (natural key, NOT NULL)  
**Grain:** One row per workspace — current state only  
**Partition:** None

**Why MERGE Standard Upsert:**  
The source is a `_latest` table — it delivers only the current state of each workspace, never historical versions. Stale re-delivery is structurally impossible. No timestamp guard is needed. Standard Upsert is the correct pattern.

**MERGE behaviour:**

sql

```sql
WHEN MATCHED     → UPDATE workspace_text, workspace_url, workspace_status
WHEN NOT MATCHED → INSERT new workspace row
-- No WHEN NOT MATCHED BY SOURCE clause
-- Rows are never deleted from silver_workspace_current
```

**Live source confirmed — May 2026:**

- 2 rows returned — Prod (<PROD_WORKSPACE_ID>) and Dev (<DEV_WORKSPACE_ID>)
- Both workspaces RUNNING
- All columns present and matching silver design — no column corrections needed
- `account_id` → `account_identifier`, `workspace_id` → `workspace_identifier`, `workspace_name` → `workspace_text`, `create_time` → `workspace_creation_timestamp`, `status` → `workspace_status`

**17 workspace IDs in billing history:**  
EDA confirmed 17 distinct `workspace_id` values in `system.billing.usage`. Only 2 are resolvable via `workspaces_latest`. The remaining 15 are decommissioned and their metadata is no longer available in the source. Billing rows for those 15 workspaces will carry a null workspace label at query time. This is a source limitation — the spend is captured correctly, only the label is unresolvable.

**FK declared:** None — `silver_workspace_current` is the referenced table, not the referencing table

---

### 7. **silver_pipeline_current — Full Overwrite with ROW_NUMBER() Deduplication**

**Source:** `system.lakeflow.pipelines`  
**PK:** `pipeline_identifier` (natural key, NOT NULL — after dedup)  
**Grain:** One row per DLT pipeline (current configuration version)  
**Partition:** None

**Why Full Overwrite with ROW_NUMBER() Deduplication:**  
`system.lakeflow.pipelines` delivers the full configuration history of every pipeline on every extract — multiple rows per `pipeline_id`. Live extract confirmed 1,000 rows across only 402 distinct pipeline IDs — 343 have multiple configuration versions, meaning 85% of pipelines have duplicates confirming stale re-delivery. `change_time` is populated for all 1,000 rows and is the only reliable timestamp — `create_time` is NULL throughout. Full Overwrite with ROW_NUMBER() Deduplication is correct — same reasoning as `silver_cluster_current`.

**Dedup before overwrite:**

sql

```sql
ROW_NUMBER() OVER (PARTITION BY pipeline_id ORDER BY change_time DESC) = 1
```

**Derived column — deleted_indicator:**

sql

```sql
deleted_indicator = CASE WHEN delete_time IS NOT NULL THEN TRUE ELSE FALSE END
```

330 deleted pipelines confirmed in live extract. Deleted pipelines are retained in silver — never excluded.

**Live source findings — May 2026:**

- 1,000 total rows — 402 distinct pipeline IDs
- 343 pipeline IDs have multiple configuration versions — 85% duplicate rate
- `change_time` populated for all 1,000 rows — confirmed dedup key
- `create_time` NULL for all 1,000 rows — cannot be used
- 330 pipelines deleted (`delete_time` populated) — retained, not excluded
- `deleted_indicator` derived as `delete_time IS NOT NULL`
- `created_by` 100% populated with email addresses — reliable owner field
- `run_as` 99.7% populated with email addresses — secondary owner field
- Pipeline types: 975 MATERIALIZED_VIEW, 14 STREAMING_TABLE, 7 ETL_PIPELINE, 2 INGESTION_PIPELINE, 2 INGESTION_GATEWAY
- `settings` and `configuration` struct columns present — serialise as JSON for auditability

**FK declared:** `workspace_identifier` → `silver_workspace_current.workspace_identifier`

---

### 8. **silver_served_entity_current — Full Overwrite with ROW_NUMBER() Deduplication**

**Source:** `system.serving.served_entities`  
**PK:** `served_entity_identifier` (natural key, NOT NULL — after dedup)  
**Grain:** One row per model serving endpoint entity (current configuration version)  
**Partition:** None

**Why Full Overwrite with ROW_NUMBER() Deduplication:**  
`system.serving.served_entities` delivers the full configuration history of every served entity on every extract — multiple rows per `served_entity_id` confirmed in earlier extracts. `change_time` is populated for all rows and is the only reliable timestamp. Full Overwrite with ROW_NUMBER() Deduplication is correct — same reasoning as `silver_cluster_current` and `silver_pipeline_current`. Full rebuild eliminates any possibility of stale rows surviving in silver.

**Dedup before overwrite:**

sql

```sql
ROW_NUMBER() OVER (PARTITION BY served_entity_id ORDER BY change_time DESC) = 1
```

**Derived column — deleted_indicator:**

sql

```sql
deleted_indicator = CASE WHEN endpoint_delete_time IS NOT NULL THEN TRUE ELSE FALSE END
```

3 deleted served entities confirmed in live extract. Deleted entities are retained in silver — never excluded.

**Live source findings — May 2026:**

- 5 total rows — 5 distinct served_entity_ids
- `change_time` populated for all 5 rows — confirmed dedup key
- 3 entities deleted (`endpoint_delete_time` populated) — retained, not excluded
- 2 entities active — 2 FOUNDATION_MODEL (System-User), all 3 CUSTOM_MODEL deleted
- `deleted_indicator` derived as `endpoint_delete_time IS NOT NULL`
- `created_by` is the owner field — email for CUSTOM_MODEL, System-User for FOUNDATION_MODEL
- FOUNDATION_MODEL rows have `created_by = System-User` — owner resolution returns UNRESOLVED at gold
- `external_model_config` and `feature_spec_config` NULL throughout — not retained
- `endpoint_delete_time` is the delete timestamp — maps to `delete_time` in silver

**FK declared:** `workspace_identifier` → `silver_workspace_current.workspace_identifier`

---
### **9. silver_query_history — Append with Watermark**

**Source:** `system.query.history`
**PK:** `query_identifier` (NOT NULL) — from `statement_id`
**Grain:** One row per query execution — all execution statuses retained (`FINISHED`, `FAILED`, `CANCELED`)
**Partition:** `query_start_hour` (derived as `DATE_TRUNC('HOUR', start_timestamp)`)

**Why Append with Watermark:**
Query execution records are immutable once written. The watermark runs on `start_timestamp`. Pattern is identical to `silver_usage_history` — records cannot be updated, only appended. All execution statuses are retained at silver (`FINISHED`, `FAILED`, `CANCELED`) — status filtering to `FINISHED` only is applied at gold. An append pattern is correct — there is nothing to update. Watermark filters to only new rows on each run, avoiding full reprocessing of the growing history.

**Watermark expression:**

```sql
start_timestamp > (
    SELECT COALESCE(
        MAX(start_timestamp),
        CAST('1900-01-01T00:00:00' AS TIMESTAMP)
    )
    FROM silver_query_history
)
```

The watermark operates at timestamp granularity. If the pipeline fails mid-run, the next run picks up from the exact last successfully loaded timestamp. No row is skipped and no row is duplicated. The COALESCE handles the first run when the table is empty.

**Partition key — `query_start_hour` derived from `start_timestamp`:**

```sql
DATE_TRUNC('HOUR', start_timestamp) AS query_start_hour
```

Partitioning on the raw `start_timestamp` TIMESTAMP with millisecond precision would create one partition per distinct timestamp value — breaking Delta metadata performance. Truncating to hour gives one partition per hour of query activity. Forward-looking design — enables intra-day analytics and hour-level joins to `silver_usage_history`.

**Derived columns added at load time:**

```sql
DATE_TRUNC('HOUR', start_timestamp)  AS query_start_hour,
CAST(start_timestamp AS DATE)        AS query_start_date
```

`query_start_date` is the join key to `gold_fact_usage` for the daily attribution formula. Both columns are derived in the SELECT — not present in the source.

**Governance exclusions:**
Two source columns are deliberately excluded from the SELECT:

- `statement_text` — may contain sensitive business data, PII, or proprietary query logic. Databricks redacts with customer-managed keys.
- `error_message` — may contain sensitive data. Failure tracking is handled via `execution_status` only. Databricks redacts with customer-managed keys.

These are not pipeline gaps — they are deliberate governance decisions documented in the table design.

**Idempotency:**
Confirmed in dev — re-running notebook 2.0 after full load produced zero duplicates. `query_identifier` verified 100% unique after full run and after re-run.

---
## Gold Tables

| Table                          | Load Pattern                                   | Trigger | Partition          | Key Decision                                                                                        |
| ------------------------------ | ---------------------------------------------- | ------- | ------------------ | --------------------------------------------------------------------------------------------------- |
| `gold_dim_workspace`           | Full Overwrite                                 | Daily   | None               | 2 active rows — full rebuild cost negligible                                                        |
| `gold_dim_sku`                 | Full Overwrite                                 | Daily   | None               | ~100 rows — full rebuild cost negligible. One row per distinct SKU                                  |
| `gold_dim_object`              | Full Overwrite                                 | Daily   | None               | Current owner only — no history tracking. Surrogate key via `xxhash64` for stability across rebuilds |
| `gold_fact_usage`              | DELETE + INSERT (Partition-selective)          | Daily   | `usage_hour`       | 268,127+ rows growing daily. Partition overwrite not available on Serverless Warehouse (SQLSTATE: 42K0I) |
| `gold_query_history`           | DELETE + INSERT (Partition-selective)          | Daily   | `query_start_hour` | 1,783,948 rows growing daily. FINISHED only. Same constraint as `gold_fact_usage` — Serverless Warehouse (SQLSTATE: 42K0I) |
| `gold_top_cost_objects_current`| No load — SQL view                             | —       | —                  | Always current — view over `gold_fact_usage` and `gold_dim_object`                                  |
| `gold_daily_spend_trend`       | No load — SQL view                             | —       | —                  | Rolling averages cannot be partitioned — view computes on demand at no storage cost                 |

---

### 9. gold_dim_workspace — Full Overwrite

**Source:** `silver_workspace_current`  
**Load Pattern:** Full Overwrite  
**Trigger:** Daily after `silver_workspace_current`  
**Type:** Dimension  
**Grain:** One row per workspace  
**PK:** `workspace_sk` - surrogate key (BIGINT NOT NULL)  
**Natural Key:** `workspace_identifier` - retained NOT NULL

**Surrogate key derivation:**

sql

```sql
xxhash64(CAST(workspace_identifier AS STRING)) AS workspace_sk
```

Deterministic across rebuilds per Silver + Gold Modeling Reference — surrogate keys in overwrite tables must use `xxhash64`, not auto-increment. Auto-increment regenerates on every run and silently breaks any fact table join that used the previous value.

**Why Full Overwrite:**  
`silver_workspace_current` delivers only the current state of each workspace, 2 active rows confirmed in live extract. Full rebuild every run is correct and costs nothing at this size. No history is needed, if a workspace is renamed the new name should reflect everywhere immediately.

**Known limitation:**  
`workspaces_latest` delivers only currently active workspaces. 15 of 17 historical workspace IDs from billing history are decommissioned and absent from source — their labels will be null at query time. Source limitation, not a pipeline issue.


| Column                 | Type            | Description                                                          |
| ---------------------- | --------------- | -------------------------------------------------------------------- |
| `workspace_sk`         | BIGINT NOT NULL | Surrogate PK — `xxhash64(CAST(workspace_identifier AS STRING))`      |
| `workspace_identifier` | STRING NOT NULL | Natural key — retained for traceability and joins                    |
| `workspace_text`       | STRING          | Display label. NULL for decommissioned workspaces absent from source |
| `workspace_url`        | STRING          | Access URL                                                           |
| `workspace_status`     | STRING          | RUNNING, PROVISIONING, FAILED, BANNED, NOT_PROVISIONED               |


---

### 10. gold_dim_sku — Full Overwrite

**Source:** `silver_list_prices_history` + derived product family mapping  
**Load Pattern:** Full Overwrite  
**Trigger:** Daily after `silver_list_prices_history`  
**Type:** Dimension  
**Grain:** One row per SKU  
**PK:** `sku_sk` — surrogate key (BIGINT NOT NULL)  
**Natural Key:** `sku_name` — retained NOT NULL

**Why gold_dim_sku:**  
`billing_origin_product` from the source is a raw Databricks system value (SQL, ALL_PURPOSE, APPS, JOBS, VECTOR_SEARCH). Product family is a derived business grouping e.g. ALL_PURPOSE and JOBS_COMPUTE grouped as "Compute", SQL as "SQL Analytics". This grouping logic belongs in a dimension, not hardcoded in every downstream query. Current unit price from `silver_list_prices_history` is also surfaced here for SKU-level cost analysis without joining back to silver.

**Surrogate key derivation:**

sql

```sql
xxhash64(CAST(sku_name AS STRING)) AS sku_sk
```

Deterministic across rebuilds — surrogate keys in overwrite tables must use `xxhash64`, not auto-increment. Auto-increment regenerates on every run and silently breaks any fact table join that used the previous value.

**Why Full Overwrite:**  
`silver_list_prices_history` fully rebuilds every run. `gold_dim_sku` reads directly from it. Since the source always delivers everything, full rebuild is the correct and simplest pattern. The table is tiny — one row per distinct SKU, approximately 50–100 rows. If a SKU is retired, the row is retained with a NULL `current_price`.


| Column                   | Type            | Description                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------ | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sku_sk`                 | BIGINT NOT NULL | Surrogate PK — `xxhash64(CAST(sku_name AS STRING))`                                                                                                                                                                                                                                                                                                                 |
| `sku_name`               | STRING NOT NULL | Natural key — Databricks SKU code                                                                                                                                                                                                                                                                                                                                   |
| `billing_origin_product` | STRING NOT NULL | Raw Databricks product category from source                                                                                                                                                                                                                                                                                                                         |
| `product_family`         | STRING          | Derived business grouping — taxonomy confirmed. Categories include Compute, SQL Analytics, Serving, Apps, Clean Rooms, DLT, Model Training, Egress, Storage, and Private Connectivity                                                                                                                                                                               |
| `current_price`          | DECIMAL(18,8)   | Most recent list price in USD from `silver_list_prices_history`. NULL for retired SKUs. DECIMAL(18,8) retains full source precision, source delivers 18 decimal places. 8 decimal places accommodates future sub-cent SKU rates (e.g. high-volume micro-billing at $0.00003750 per unit) where lower precision would introduce rounding error in cost calculations. |


---

### 11. gold_dim_object — Full Overwrite

**Source:** `silver_usage_history` + `silver_cluster_current` + `silver_warehouse_current` + `silver_job_current` + `silver_pipeline_current` + `silver_served_entity_current`  
**Load Pattern:** Full Overwrite  
**Trigger:** Daily   
**Type:** Dimension  
**Grain:** One row per billable object (current state)  
**PK:** `object_sk` — surrogate key (BIGINT NOT NULL)  
**Natural Key:** `object_identifier + object_type` — both retained NOT NULL

**Why Full Overwrite:**  
One row per billable object reflecting current state. Every daily run rebuilds the full dimension from the six silver metadata tables. Owner reflects whoever owns the object today. No ownership history is tracked — historical ownership attribution is out of scope for this pipeline.

**Surrogate key derivation:**

sql

```sql
xxhash64(
    CAST(object_identifier AS STRING) || '||' ||
    CAST(object_type       AS STRING)
) AS object_sk
```

Deterministic across daily rebuilds — one surrogate key per object, stable across runs. `xxhash64` used per Silver + Gold Modeling Reference — auto-increment would regenerate on every Full Overwrite and silently break any fact table join.

**Owner resolution — COALESCE priority chain:**

sql

```sql
COALESCE(executed_by_identity, creator_email, owner_email)
```

Resolution attempted in priority order. Coverage confirmed from live source data:


| Priority | Field                  | Silver Source                                       | Coverage                                            |
| -------- | ---------------------- | --------------------------------------------------- | --------------------------------------------------- |
| 1st      | `executed_by_identity` | `silver_usage_history` — `identity_metadata.run_as` | 27.7% populated — email or service principal, mixed |
| 2nd      | `creator_email`        | `silver_pipeline_current` — `created_by`            | 100% email confirmed                                |
| 2nd      | `creator_email`        | `silver_job_current` — `creator_user_name`          | 11.9% email, 88.1% null                             |
| 3rd      | `owner_email`          | `silver_cluster_current` — `owned_by`               | 100% email confirmed                                |


`creator_identity` from `silver_warehouse_current` and `silver_served_entity_current` is not included in the primary COALESCE chain — it contains mixed values (emails, numeric system IDs, `System-User`) and is retained in silver for lineage only.

**Attribution method values:**

- `executed_by_identity` — resolved from `identity_metadata.run_as` in `silver_usage_history`
- `creator_email` — resolved from `silver_pipeline_current.created_by` or `silver_job_current.creator_user_name`
- `owner_email` — resolved from `silver_cluster_current.owned_by`
- `UNRESOLVED` — all COALESCE sources NULL. Applies to serverless SQL warehouse queries (NULL by Databricks platform design), FOUNDATION_MODEL endpoints (System-User), and objects whose metadata was absent before capture

**Columns:**


| Column               | Type            | Description                                                                                                                                           |
| -------------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `object_sk`          | BIGINT NOT NULL | Surrogate PK — `xxhash64(object_identifier || object_type)`. Stable across daily rebuilds                                                             |
| `object_identifier`  | STRING NOT NULL | Natural key component — billable object identifier                                                                                                    |
| `object_type`        | STRING NOT NULL | Natural key component — CLUSTER, WAREHOUSE, JOB, PIPELINE, ENDPOINT                                                                                   |
| `object_text`        | STRING          | Human-readable label from silver metadata. NULL for deleted objects                                                                                   |
| `owner_identity`     | STRING          | Resolved identity from COALESCE chain. Email for human owners. Service principal or system identifier for non-human identities. NULL where UNRESOLVED |
| `attribution_method` | STRING NOT NULL | How owner was resolved — `executed_by_identity`, `creator_email`, `owner_email`, `UNRESOLVED`                                                         |
| `workspace_sk`       | BIGINT NOT NULL | FK → `gold_dim_workspace.workspace_sk`                                                                                                                |
| `last_activity_date` | DATE            | MAX(`usage_date`) across all billing records for this object. Recalculated on every daily Full Overwrite run                                          |
| `idle_day_count`     | INT             | `DATEDIFF(CURRENT_DATE(), last_activity_date)`. Recalculated on every daily Full Overwrite run                                                        |
| `deleted_indicator`  | BOOLEAN         | TRUE when object identifier absent from all silver metadata tables after dedup                                                                        |


---

### 12. gold_fact_usage — Partition / Predicate-based Overwrite

**Source:** `silver_usage_history`  
**Load Pattern:** Partition / Predicate-based Overwrite on `usage_hour`  
**Trigger:** Daily  
**Type:** Fact  
**Grain:** One row per `workspace_sk × object_sk × sku_sk × usage_hour`  
**PK:** `workspace_sk + object_sk + sku_sk + usage_hour` (composite)  
**Partition:** `usage_hour`

Central hourly spend fact table. Carries all additive measures per Silver + Gold Modeling Reference — no descriptive attributes. Object names, owner identity, and workspace labels are resolved by joining to dimension tables at query time.

**Why Partition / Predicate-based Overwrite:**  
The table is fully recomputable from silver on every run. Each hourly partition is independent — no window function spans partitions. INSERT OVERWRITE replaces only the partitions present in the source SELECT, leaving all historical partitions untouched. The table is never dropped.

**Why object_sk is on the fact:**  
Including `object_sk` at the fact grain enables direct join to `gold_dim_object` for object name, owner identity, idle status, and deletion flag — resolved at query time. One surrogate key per object — stable across daily Full Overwrite rebuilds of `gold_dim_object`.

**Tag columns on fact:**  
`tag_team_text`, `tag_domain_text`, `tag_purpose_text` are carried as flat measure-context columns. Unpivoting to a tag dimension would create a 3× row fan-out per usage record and complicate the grain. Three tag keys are low cardinality and filter efficiently as flat columns.

**Rolling averages** are computed at query time via `gold_daily_spend_trend` view — not pre-stored on this table. Pre-storing rolling averages would require Full Overwrite because the window spans all partitions.


| Column                 | Type               | Description                                                                                                                                                                                                                                   |
| ---------------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `usage_hour`           | TIMESTAMP NOT NULL | Hourly partition key — derived as `DATE_TRUNC('HOUR', usage_start_timestamp)`                                                                                                                                                                 |
| `usage_date`           | DATE NOT NULL      | Calendar date — retained for date-level filtering and joins                                                                                                                                                                                   |
| `workspace_sk`         | BIGINT NOT NULL    | FK → `gold_dim_workspace.workspace_sk`                                                                                                                                                                                                        |
| `object_sk`            | BIGINT NOT NULL    | FK → `gold_dim_object.object_sk`                                                                                                                                                                                                              |
| `sku_sk`               | BIGINT NOT NULL    | FK → `gold_dim_sku.sku_sk`                                                                                                                                                                                                                    |
| `tag_team_text`        | STRING             | Value of the team tag. UNTAGGED sentinel for null                                                                                                                                                                                             |
| `tag_domain_text`      | STRING             | Value of the domain tag, normalised. UNTAGGED sentinel for null                                                                                                                                                                               |
| `tag_purpose_text`     | STRING             | Value of the purpose tag. UNTAGGED sentinel for null                                                                                                                                                                                          |
| `total_cost`           | DECIMAL(18,2)      | `SUM(usage_cost)` from `silver_usage_history` for this grain row. Cost in USD at standard list price                                                                                                                                          |
| `total_usage_quantity` | DECIMAL(18,6)      | `SUM(usage_quantity)` from `silver_usage_history` for this grain row. `DECIMAL(18,6)` matches source precision — 6 decimal places retains full fidelity of the raw usage quantity measure. Unit varies by SKU — DBU, GB, HOUR, DAY, GPU_HOUR. |
| `billing_row_count`    | BIGINT             | COUNT of `silver_usage_history` rows in this aggregation                                                                                                                                                                                      |


---

### **gold_query_history — DELETE + INSERT (Partition-selective)**

**Source:** `silver_query_history` LEFT JOIN `silver_warehouse_current` LEFT JOIN `silver_workspace_current`
**PK:** `query_identifier` (NOT NULL)
**Grain:** One row per FINISHED query execution
**Partition:** `query_start_hour`

**Why DELETE + INSERT (not Full Overwrite):**
At 1,783,948 rows and growing daily, Full Overwrite rewrites the entire table on every run. DELETE + INSERT only touches partitions in the daily watermark window (typically 24–48 hours), leaving all historical partitions untouched. Identical pattern and constraint to `gold_fact_usage` — `spark.sql.sources.partitionOverwriteMode` is not available on Serverless Warehouse (SQLSTATE: 42K0I).

**Why not Partition Overwrite:**
REPLACE WHERE with subquery not supported (SQLSTATE: 0A000). `spark.sql.sources.partitionOverwriteMode` not available on Serverless Warehouse (SQLSTATE: 42K0I).

**Load window gap:**
Between DELETE completing and INSERT completing, affected partitions have zero rows in gold. Dashboard queries landing in this window get incomplete results for those hours. Acceptable for a daily batch pipeline — schedule dashboards to refresh after pipeline completes.

**DELETE step:**

```sql
DELETE FROM gold_query_history
WHERE query_start_hour IN (
    SELECT DISTINCT query_start_hour
    FROM silver_query_history
    WHERE start_timestamp > (
        SELECT COALESCE(
            MAX(start_timestamp),
            CAST('1900-01-01T00:00:00' AS TIMESTAMP)
        )
        FROM gold_query_history
    )
)
```

**INSERT step:**
Selects from `silver_query_history WHERE execution_status = 'FINISHED'`. LEFT JOINs `warehouse_name` from `silver_warehouse_current` and `workspace_name` from `silver_workspace_current`. Denormalized columns eliminate joins in the dashboard layer. NULL accepted for deleted warehouses (11.72% of `warehouse_name`) — expected and documented.

**Why FINISHED only:**
FAILED queries consume 0.0102% of total task seconds (9.6s out of 93,761.9s) — confirmed negligible by profiling. CANCELED = 0 observed across all Claude MCP queries. Whitelist approach — any new or unknown status is automatically excluded until explicitly evaluated.

**First run behaviour:**
Table empty — watermark = 1900-01-01 — DELETE finds nothing — INSERT loads all FINISHED rows from silver. Safe. Set `initial_full_load = True` on first run to confirm.

**Idempotency:**
Confirmed in dev — re-running notebook 3.0 after full load produced zero duplicates. `query_identifier` verified 100% unique after full run and after re-run. Silver → gold row difference = 0.

**Denormalization:**

| Denormalized Column | Source Table                  | Null %  | Reason                                              |
| ------------------- | ----------------------------- | ------- | --------------------------------------------------- |
| `warehouse_name`    | `silver_warehouse_current`    | 11.72%  | Deleted or decommissioned warehouses — expected     |
| `workspace_name`    | `silver_workspace_current`    | ~0%     | Only 2 active workspaces — near-full coverage       |

---

### 13. gold_top_cost_objects_current — View

**Type:** View (`gold_<view_name>` convention)  
**Definition:** `gold_fact_usage` JOIN `gold_dim_object` JOIN `gold_dim_workspace`  
**No load pattern — SQL view, always current.**

Per Silver + Gold Modeling Reference: "Filter or reshape of gold with no new computation → SQL view." This view joins the fact table to `gold_dim_object` and `gold_dim_workspace`, aggregates lifetime spend per object, and ranks by total cost. It is always current because it reads live from the underlying tables.

**View logic:**

sql

```sql
CREATE OR REPLACE VIEW gold_top_cost_objects_current AS
SELECT
    o.object_identifier,
    o.object_type,
    o.object_text,
    o.owner_identity,
    o.attribution_method,
    o.workspace_sk,
    w.workspace_text,
    o.last_activity_date,
    o.idle_day_count,
    o.deleted_indicator,
    SUM(f.total_cost)                             AS total_cost,
    RANK() OVER (ORDER BY SUM(f.total_cost) DESC) AS cost_rank
FROM gold_fact_usage         f
JOIN gold_dim_object         o ON f.object_sk = o.object_sk
LEFT JOIN gold_dim_workspace w ON o.workspace_sk = w.workspace_sk
GROUP BY
    o.object_identifier,
    o.object_type,
    o.object_text,
    o.owner_identity,
    o.attribution_method,
    o.workspace_sk,
    w.workspace_text,
    o.last_activity_date,
    o.idle_day_count,
    o.deleted_indicator
```

**Answers:** BQ3 (top cost objects), BQ4 (ownership and idle status)

---

### 14. gold_daily_spend_trend — View

**Type:** View (`gold_<view_name>` convention)  
**Definition:** Daily aggregation of `gold_fact_usage` from hourly grain with rolling average window functions  
**No load pattern — SQL view, always current.**

Rolling averages cannot be partitioned — the 30-day window spans all partitions. Storing them on `gold_fact_usage` would force a Full Overwrite on that table, destroying the partition overwrite benefit. A view computes them on demand at no storage cost and with no job task. The view also serves as the daily aggregation layer — rolling up from the hourly `gold_fact_usage` grain to daily totals.

**View logic:**

sql

```sql
CREATE OR REPLACE VIEW gold_daily_spend_trend AS
SELECT
    f.usage_date,
    SUM(f.total_usage_quantity)                                        AS total_usage_quantity,
    SUM(f.total_cost)                                                  AS daily_cost,
    AVG(SUM(f.total_cost)) OVER (
        ORDER BY f.usage_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    )                                                                  AS rolling_30_day_avg_cost,
    AVG(SUM(f.total_cost)) OVER (
        ORDER BY f.usage_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    )                                                                  AS rolling_7_day_avg_cost
FROM gold_fact_usage f
GROUP BY f.usage_date
ORDER BY f.usage_date
```

**Answers:** BQ2 (daily trend, rolling averages, forecast basis)

---

## Star Schema

```
gold_dim_workspace              gold_dim_sku                    gold_dim_object
──────────────────              ────────────                    ───────────────
workspace_sk      (PK)          sku_sk           (PK)           object_sk          (PK)
workspace_identifier (NK)       sku_name         (NK)           object_identifier  (NK)
workspace_text                  billing_origin_product          object_type        (NK)
workspace_url                   product_family                  object_text
workspace_status                current_price                   owner_identity
                                                                attribution_method
                                                                workspace_sk  (FK → gold_dim_workspace)
                                                                last_activity_date
                                                                idle_day_count
                                                                deleted_indicator
        │                              │                              │
        └──────────────────────────────┼──────────────────────────────┘
                                       │
                          gold_fact_usage  (Partition / usage_hour)
                          ──────────────────────────────────────────
                          usage_hour            (PK + partition)
                          usage_date            (date-level filtering)
                          workspace_sk          (FK → gold_dim_workspace)
                          object_sk             (FK → gold_dim_object)
                          sku_sk                (FK → gold_dim_sku)
                          tag_team_text
                          tag_domain_text
                          tag_purpose_text
                          total_cost
                          total_usage_quantity
                          billing_row_count

                                       │
                       ┌───────────────┴───────────────┐
                       │                               │
       gold_top_cost_objects_current      gold_daily_spend_trend
            (VIEW — no storage)               (VIEW — no storage)
```

---

## Business Questions — Query Map

| BQ  | Question                                       | Query approach                                                                                                                                                                                                                    |
| --- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| BQ1 | Total spend by workspace / product / SKU       | `SELECT f.usage_date, w.workspace_text, s.product_family, s.sku_name, SUM(f.total_cost) AS total_cost FROM gold_fact_usage f LEFT JOIN gold_dim_workspace w ON f.workspace_sk = w.workspace_sk LEFT JOIN gold_dim_sku s ON f.sku_sk = s.sku_sk GROUP BY f.usage_date, w.workspace_text, s.product_family, s.sku_name` |
| BQ2 | Daily trend and rolling averages               | `SELECT * FROM gold_daily_spend_trend`                                                                                                                                                                                            |
| BQ3 | Top 10 cost objects by spend                   | `SELECT * FROM gold_top_cost_objects_current WHERE cost_rank <= 10`                                                                                                                                                               |
| BQ4 | Object ownership, attribution, and idle status | `SELECT object_text, object_type, owner_identity, attribution_method, idle_day_count, deleted_indicator FROM gold_top_cost_objects_current`                                                                                       |
| BQ5 | Spend by tag                                   | `SELECT tag_domain_text, SUM(total_cost) AS total_cost FROM gold_fact_usage GROUP BY tag_domain_text`                                                                                                                             |
| BQ6 | Attribution coverage                           | `SELECT o.attribution_method, SUM(f.total_cost) AS total_cost FROM gold_fact_usage f JOIN gold_dim_object o ON f.object_sk = o.object_sk GROUP BY o.attribution_method`                                                          |
| BQ7 | Claude estimated attributed cost by warehouse and day | Applied in Power BI DAX against `gold_query_history` (Claude task seconds) and `gold_fact_usage` (total warehouse cost). Filter: `client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')` |
| BQ8 | Claude query count and active users by month   | `SELECT DATE_TRUNC('MONTH', query_start_date), COUNT(*) AS query_count, COUNT(DISTINCT executed_by_identity) AS distinct_users FROM gold_query_history WHERE client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp') GROUP BY 1 ORDER BY 1` |
| BQ9 | Cache hit rate for Claude queries              | `SELECT result_cache_hit_indicator, COUNT(*) AS query_count FROM gold_query_history WHERE client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp') GROUP BY result_cache_hit_indicator` |
---

## Open Items

| #  | Item | Detail | Owner |
| --- | --- | --- | --- |
| 1 | `silver_usage_history` watermark assumption — CLOSED | Resolved. Correction rows (RETRACTION / RESTATEMENT) are possible per Databricks documentation but 0 observed across 268,127 rows in EDA. A strict forward-only watermark could miss correction rows if the corrected timestamp falls behind the current watermark position. Risk accepted and documented. Reopen if correction rows are observed in future. | Closed |
| 2 | `product_family` mapping for `gold_dim_sku` | Taxonomy needs reviewer sign-off before `gold_dim_sku` notebook. Live list_prices data confirms broader categories — Compute, SQL Analytics, Serving, Apps, Clean Rooms, DLT, Model Training, Egress, Storage, Private Connectivity. | Data + Automation Team |
| 3 | `silver_workspace_current` — null labels for 15 workspaces | EDA confirmed 17 distinct `workspace_id` values in `system.billing.usage`. `workspaces_latest` returns only 2 active workspaces. 15 decommissioned workspace IDs have no metadata available — their workspace label will be null at query time. Source limitation — no pipeline action required. | Documented — no action |
| 4 | All load pattern decisions + 2 views sign-off | Full review and sign-off required before Child 3 notebook work begins. | Data + Automation Team |
| 5 | Job task chain | Parallel silver tasks (Tasks 3–8) confirmed — no cross-dependency between metadata silver tables. | Data + Automation Team |
| 6 | `silver_job_current` owner attribution | No reliable email owner field in `system.lakeflow.jobs`. `creator_user_name` NULL for 94% of rows. `creator_id` and `run_as` hold system IDs not emails. Job cost objects will return UNRESOLVED at gold for most rows. Confirm whether identity resolution step needed before gold notebook is written. | Data + Automation Team |
| 7 | CANCELED query monitoring | Zero CANCELED Claude queries observed across full pipeline load. If CANCELED appears in future, profile `total_task_duration_ms` before including in `gold_query_history` filter. Suggested future filter: `WHERE execution_status IN ('FINISHED', 'CANCELED')`. | Data + Automation — Monitor |
| 8 | `system.query.history` retention policy | Databricks default retention is 30 days. Silver watermark covers history from February 2026. Confirm the account retention policy with Databricks admin to ensure no gap risk. | Databricks admin — Confirm |
| 9 | New Claude client application strings | Two strings currently identified: `Databricks SQL MCP` and `DatabricksDbsqlMcp`. If Anthropic or Databricks introduce new MCP client strings, update the dashboard filter IN clause. No pipeline change required. | Data + Automation — Monitor |
| 10 | `warehouse_name` 11.72% null in `gold_query_history` | Deleted or decommissioned warehouses no longer present in `silver_warehouse_current`. LEFT JOIN returns NULL. Expected and documented — no pipeline action required. | Documented — no action |
| 11 | `statement_text` governance | Excluded from `silver_query_history` — may contain sensitive data. If needed for future query pattern analysis, establish a governed access process before adding to silver. | Data Governance — Future |


---

## Decisions Log

| Table | Standard default | Decision | Rationale |
| --- | --- | --- | --- |
| `silver_usage_history` | MERGE Standard Upsert | Append with Watermark | Records immutable. Watermark is simpler and more efficient at 268,127 rows. Correction row risk accepted and documented — 0 observed in EDA. |
| `silver_cluster_current` | MERGE Conditional (Timestamp-Guarded) | Full Overwrite with ROW_NUMBER() Deduplication | Live extract confirmed `last_restarted_time` absent from source. `change_time` is the only reliable timestamp, populated for all 1,000 rows. Full rebuild eliminates stale rows without a MERGE guard. `deleted_indicator` derived as `delete_time IS NOT NULL`. |
| `silver_warehouse_current` | MERGE Conditional (Timestamp-Guarded) | Full Overwrite with ROW_NUMBER() Deduplication | Live extract confirmed `last_modified_time` absent. `change_time` populated for all 30 rows. Same pattern as `silver_cluster_current`. `deleted_indicator` derived as `delete_time IS NOT NULL`. |
| `silver_job_current` | MERGE Conditional (Timestamp-Guarded) | Full Overwrite with ROW_NUMBER() Deduplication | `change_time` only reliable timestamp. `creator_user_name` NULL for 941 rows — no reliable email owner. System IDs in `creator_id` and `run_as` not suitable for attribution. Open item raised. `deleted_indicator` derived as `delete_time IS NOT NULL`. |
| `silver_pipeline_current` | MERGE Conditional (Timestamp-Guarded) | Full Overwrite with ROW_NUMBER() Deduplication | `create_time` NULL for all 1,000 rows — only `change_time` usable. 85% duplicate rate confirmed. `deleted_indicator` derived as `delete_time IS NOT NULL`. |
| `silver_served_entity_current` | MERGE Conditional (Timestamp-Guarded) | Full Overwrite with ROW_NUMBER() Deduplication | Multiple config versions per entity confirmed. `change_time` only reliable timestamp. `endpoint_delete_time` mapped to `delete_time`. `deleted_indicator` derived as `endpoint_delete_time IS NOT NULL`. |
| All `_current` metadata tables | `is_deleted` boolean | `deleted_indicator` | Per the internal data naming standard — `_indicator` suffix is the correct representation for boolean values. Object class prefix omitted as redundant within each table's own context. |
| All silver metadata tables | Old names without suffix | `_history` / `_current` suffixes | Per Unity Catalog naming standard — `_history` for tables that accumulate over time, `_current` for tables that hold one row per entity at current state. |
| `gold_dim_object` | Insert Overwrite | Full Overwrite | No ownership history tracking required for this pipeline — current owner only. Historical ownership attribution is out of scope. SCD Type 2 columns (`valid_from`, `valid_to`, `active_indicator`) removed. |
| `gold_dim_workspace` | `is_active` column | Column removed | `workspace_status` already provides active/inactive state directly. Derived boolean flag adds no value and was removed. |
| `gold_dim_sku` | SKU flat on fact | Dedicated dimension | Product family is a derived business grouping that does not exist in the source. Belongs in a dimension, not hardcoded in every query. Current price surfaced here without joining back to silver. |
| `gold_fact_usage` — grain | Daily | Hourly (`usage_hour`) | Source is hourly grain per Databricks documentation — each billing row represents up to one hour of compute. Gold retains hourly grain. Daily aggregation and rolling averages handled in `gold_daily_spend_trend` view. |
| `gold_fact_usage` — `object_sk` on grain | No object at fact grain | `object_sk` included | Enables direct join to `gold_dim_object` for object name, owner identity, idle status, and deletion flag at query time. |
| `gold_fact_usage` — rolling averages | Pre-stored columns | `gold_daily_spend_trend` view | Pre-storing rolling averages forces Full Overwrite (window spans all partitions). View computes on demand at no storage cost and also handles daily aggregation from hourly grain. |
| `gold_fact_usage` — tag columns | Tag dimension table | Flat columns on fact | Unpivoting 3 tag keys creates 3× row fan-out and complicates the grain. Low-cardinality flat columns filter efficiently at query time. |
| `gold_top_cost_objects_current` | Aggregation table | SQL view — no storage | View over `gold_fact_usage` and `gold_dim_object` is always current and requires no job task. |
| `silver_usage_history` — cost derivation | Cost at gold view | `usage_cost` at silver load time | `silver_usage_history` joins to `silver_list_prices_history` at load time and computes `usage_cost = usage_quantity × pricing.default` per billing record. `pricing.default` used per Databricks documentation — officially endorsed field for cost calculation. Promotional rates not applied — deliberate decision accepted and documented. |
| `gold_daily_spend_trend` — daily cost | Pre-stored on fact | Derived in view | `daily_cost = SUM(usage_cost)` aggregated from hourly fact grain to daily in the view. Keeps fact table at hourly grain while providing daily totals for reporting. |
| `silver_query_history` — load pattern | MERGE Standard Upsert | Append with Watermark on `start_timestamp` | Records immutable. Pattern identical to `silver_usage_history`. All statuses retained at silver — filtering to FINISHED only applied at gold. |
| `silver_query_history` — governance exclusions | Retain all source columns | Exclude `statement_text` and `error_message` | Both columns may contain sensitive business data or PII. Databricks redacts with customer-managed keys. Failure tracking handled via `execution_status` only. Deliberate decision — not a pipeline gap. |
| `silver_query_history` — partition key | None / raw timestamp | `query_start_hour` via `DATE_TRUNC('HOUR', start_timestamp)` | Raw timestamp with millisecond precision would create one partition per distinct value — breaks Delta metadata performance. Hourly truncation aligns with `silver_usage_history` partition strategy. |
| `gold_query_history` — load pattern | Full Overwrite | DELETE + INSERT (partition-selective on `query_start_hour`) | 1,783,948 rows and growing daily. Partition-selective is efficient — only touches daily watermark window. `spark.sql.sources.partitionOverwriteMode` not available on Serverless Warehouse (SQLSTATE: 42K0I). |
| `gold_query_history` — status filter | All statuses | FINISHED only | FAILED = 0.0102% of total task seconds (9.6s out of 93,761.9s) — confirmed negligible by profiling. CANCELED = 0 observed. Whitelist approach — new statuses automatically excluded until evaluated. |
| `gold_query_history` — partition key | None / daily | Hourly (`query_start_hour`) | Forward-looking design for intra-day analytics. Enables hour-level joins to `silver_usage_history`. Consistent with `silver_query_history` partition key. |
| `gold_query_history` — denormalization | Join at query time | `warehouse_name` + `workspace_name` at load time | Eliminates joins in the Power BI dashboard layer. NULL accepted for deleted warehouses (11.72%) — expected and documented. |
| Claude query identification | Derived boolean column in pipeline | Filter `client_application` in dashboard layer | Transparent and maintainable. Two confirmed client strings: `Databricks SQL MCP` and `DatabricksDbsqlMcp`. Adding new strings in future = dashboard change only, no pipeline change required. |
| Attribution metric | `total_duration_ms` (wall-clock) | `total_task_duration_ms` | Reflects true parallel compute consumption across all CPU cores. Wall-clock overstates actual compute by ~23% for Claude queries. `execution_duration_ms` has 9.69% null rate — not suitable for attribution. |
| Attribution grain | Monthly per warehouse | Daily per warehouse, then summed to monthly | Monthly grain inflates results on shared warehouses with volatile daily Claude shares. Confirmed during methodology review: monthly grain = $904 vs correct daily grain = $462. |
| `cost_per_session` | Include as a metric | Excluded | `session_identifier = query_identifier` throughout Claude MCP. Cost-per-session is identical to cost-per-query — redundant metric adds no value. |

---

## References

- Databricks SQL Load Patterns Reference — Process Standards 
- Silver + Gold Modeling Reference — Process Standards 
- Architecture and Catalog Guide — Process Standards 
- Databricks Job Standards — Process Standards