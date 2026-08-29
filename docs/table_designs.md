# Table Design Proposal

## Databricks Cost Analytics Pipeline

**Pipeline:** Databricks Cost Analytics  
**Domain:** data_automation  
**Schema:** databricks_analytics  
**Author:** Tushar — Data + Automation Team  
**Date:** May 2026  
**Status:** In-review  
**File path:** `domains/data_automation/databricks_analytics/docs/table_designs.md`

---

## Purpose

This document defines the silver layer table design for the Databricks Cost Analytics pipeline. It covers every silver table, its grain, source, load pattern, primary key, foreign keys, column list, and design rationale. The column list and names in this document are the authoritative source for the silver DDL. The DDL must match this document exactly.

The gold layer will be appended to this document.

---

## Source System

All silver tables read directly from Databricks system tables. There is no bronze layer. System tables are Unity Catalog native  they are not ingested from an external source system. The pipeline reads from two namespaces:

- `system.billing` — billing usage events and SKU list prices
- `system.compute` — cluster and SQL warehouse metadata
- `system.lakeflow` — job and DLT pipeline metadata
- `system.access` — workspace metadata
- `system.serving` — model serving endpoint metadata

---

## Silver Layer Overview

The silver layer holds 8 tables - 2 history tables and 6 current-state tables. All follow the 3NF entity model per the Silver + Gold Modeling Reference. No aggregation at silver. Natural keys only, no surrogate keys.


| Table                          | Suffix     | Source                            | Grain                                                             | Load Pattern                        |
| ------------------------------ | ---------- | --------------------------------- | ----------------------------------------------------------------- | ----------------------------------- |
| `silver_usage_history`         | `_history` | `system.billing.usage`            | One row per billing usage record                                  | Append with Watermark               |
| `silver_list_prices_history`   | `_history` | `system.billing.list_prices`      | One row per SKU per price effective period                        | Full Overwrite                      |
| `silver_cluster_current`       | `_current` | `system.compute.clusters`         | One row per cluster (current configuration)                       | Full Overwrite + ROW_NUMBER() Dedup |
| `silver_warehouse_current`     | `_current` | `system.compute.warehouses`       | One row per SQL warehouse (current configuration)                 | Full Overwrite + ROW_NUMBER() Dedup |
| `silver_job_current`           | `_current` | `system.lakeflow.jobs`            | One row per job (current configuration)                           | Full Overwrite + ROW_NUMBER() Dedup |
| `silver_workspace_current`     | `_current` | `system.access.workspaces_latest` | One row per workspace (current state)                             | Full Overwrite  |
| `silver_pipeline_current`      | `_current` | `system.lakeflow.pipelines`       | One row per DLT pipeline (current configuration)                  | Full Overwrite + ROW_NUMBER() Dedup |
| `silver_served_entity_current` | `_current` | `system.serving.served_entities`  | One row per model serving endpoint entity (current configuration) | Full Overwrite + ROW_NUMBER() Dedup |
| silver_query_history | _history | system.query.history | One row per query execution (all execution statuses) | Append with Watermark |


**Suffix convention:** `_history` tables accumulate records over time. `_current` tables hold one row per entity at current state. Per Unity Catalog naming standard.

---

## Foreign Key Relationships

`silver_workspace_current` is the anchor table. Five of the seven remaining tables declare a foreign key to it.

```
silver_workspace_current (workspace_identifier)
    ← silver_usage_history.workspace_identifier
    ← silver_cluster_current.workspace_identifier
    ← silver_warehouse_current.workspace_identifier
    ← silver_job_current.workspace_identifier
    ← silver_pipeline_current.workspace_identifier
    ← silver_served_entity_current.workspace_identifier
    ← silver_query_history.workspace_identifier
silver_list_prices_history — no FK (standalone reference table)
```

---

## Table Designs

---

### **1. silver_usage_history**

**Source:** `system.billing.usage`  
**Grain:** One row per billing usage record — source aggregated by hour. Each row represents up to one hour of compute activity. Runs longer than one hour produce multiple rows, one per clock-hour boundary.  
**PK:** `record_identifier` (natural key, NOT NULL)  
**FK:** `workspace_identifier` → `silver_workspace_current.workspace_identifier`  
**Partition:** `usage_hour` (derived as `DATE_TRUNC('HOUR', usage_start_timestamp)`)  
**Load pattern:** Append with Watermark  
**Task:** 2 (no upstream dependency — runs in parallel with Task 1)

**Purpose:**  
Central fact table at silver. Every Databricks compute billing event since August 2023 lives here — 268,127 rows growing daily. Records are immutable once written. The table unpacks all nested structs from the source into flat columns and extracts the three standard tag values. No cost derivation at silver — `usage_quantity` is the raw measure. Hourly and daily cost are derived at the gold view layer by joining to `silver_list_prices_history` at query time.

**Key source findings:**

- 268,127 rows / 0 duplicates / 0 correction rows confirmed in EDA
- Source aggregated by hour per Databricks documentation — hourly grain confirmed
- Records are immutable — strict Append with Watermark is safe
- No cost derivation at silver — cost calculation separated into gold view layer
- Correction rows (RETRACTION / RESTATEMENT) are possible per Databricks documentation but 0 observed across 268,127 rows in EDA. Risk accepted and documented — revisit if correction rows appear in future
- Partial hour exclusion not handled at silver load time — handled at dashboarding layer
- `usage_type` values per Databricks documentation: COMPUTE_TIME, STORAGE_SPACE, NETWORK_BYTE, NETWORK_HOUR, API_OPERATION, TOKEN, GPU_TIME, ANSWER

**Columns:**


| Column                            | Data Type          | Nullable | Notes                                                                                           |
| --------------------------------- | ------------------ | -------- | ----------------------------------------------------------------------------------------------- |
| `record_identifier`               | STRING             | NOT NULL | PK — from `record_id`                                                                           |
| `account_identifier`              | STRING             | NOT NULL | from `account_id`                                                                               |
| `workspace_identifier`            | STRING             | NOT NULL | FK → `silver_workspace_current`                                                                 |
| `sku_name`                        | STRING             | NOT NULL | joins to `silver_list_prices_history` for cost calculation at gold                              |
| `cloud`                           | STRING             | NULL     | AZURE throughout                                                                                |
| `usage_date`                      | DATE               | NOT NULL | from source `usage_date` — retained for date-level filtering                                    |
| `usage_hour`                      | TIMESTAMP          | NOT NULL | partition key — derived as `DATE_TRUNC('HOUR', usage_start_timestamp)`                          |
| `usage_start_timestamp`           | TIMESTAMP          | NOT NULL | watermark column — from `usage_start_time`                                                      |
| `usage_end_timestamp`             | TIMESTAMP          | NULL     | from `usage_end_time`                                                                           |
| `usage_quantity`                  | DECIMAL(18,6)      | NULL     | raw DBU / GB / HOUR quantity — cost derived at gold view                                        |
| `usage_unit`                      | STRING             | NULL     | DBU, GB, HOUR, DAY, DSU, GPU_HOUR                                                               |
| `billing_origin_product`          | STRING             | NULL     | JOBS, DLT, SQL, ALL_PURPOSE, MODEL_SERVING, APPS etc.                                           |
| `usage_type`                      | STRING             | NULL     | COMPUTE_TIME, STORAGE_SPACE, NETWORK_BYTE, NETWORK_HOUR, API_OPERATION, TOKEN, GPU_TIME, ANSWER |
| `record_type`                     | STRING             | NULL     | ORIGINAL, RETRACTION, RESTATEMENT                                                               |
| `cluster_identifier`              | STRING             | NULL     | from `usage_metadata.cluster_id`                                                                |
| `warehouse_identifier`            | STRING             | NULL     | from `usage_metadata.warehouse_id`                                                              |
| `job_identifier`                  | STRING             | NULL     | from `usage_metadata.job_id`                                                                    |
| `declarative_pipeline_identifier` | STRING             | NULL     | from `usage_metadata.dlt_pipeline_id`                                                           |
| `endpoint_identifier`             | STRING             | NULL     | from `usage_metadata.endpoint_id`                                                               |
| `job_name`                        | STRING             | NULL     | from `usage_metadata.job_name`                                                                  |
| `executed_by_identity`            | STRING             | NULL     | from `identity_metadata.run_as`                                                                 |
| `tag_team_text`                   | STRING             | NULL     | from `custom_tags['team']`                                                                      |
| `tag_domain_text`                 | STRING             | NULL     | from `custom_tags['domain']`                                                                    |
| `tag_purpose_text`                | STRING             | NULL     | from `custom_tags['purpose']`                                                                   |
| `custom_tags`                     | MAP<STRING,STRING> | NULL     | full tag map retained                                                                           |


---

### 2. silver_list_prices_history

**Source:** `system.billing.list_prices`  
**Grain:** One row per SKU per price effective period  
**PK:** `sku_name + price_start_timestamp` (composite natural key, both NOT NULL)  
**FK:** None — standalone reference table  
**Load pattern:** Full Overwrite  
**Task:** 1 (no upstream dependency — runs in parallel with Task 2)

**Purpose:**  
Standalone price reference table. The source delivers the complete price history for every SKU on every extract. Full Overwrite every run — the table is small (~100 rows) and the full rebuild cost is negligible. Not joined at silver load time — the gold view `gold_daily_spend_trend` joins this table to `silver_usage_history` at query time to derive hourly and daily cost using `pricing.default` as the unit price.

**Key source findings:**

- Prices change over time per SKU 
- `pricing.default` is the published standard list price per Databricks documentation and the officially endorsed field for cost calculation. Promotional rates not applied — during promotional periods actual billed amount may be lower. Deliberate design decision accepted and documented
- `pricing_json` retained for auditability — contains full pricing struct including default, promotional, and effective list rates

**Columns:**


| Column                  | Data Type     | Nullable | Notes                                                                                                                                        |
| ----------------------- | ------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `sku_name`              | STRING        | NOT NULL | PK component — Databricks SKU code                                                                                                           |
| `price_start_timestamp` | TIMESTAMP     | NOT NULL | PK component — lower bound of price effective period                                                                                         |
| `price_end_timestamp`   | TIMESTAMP     | NULL     | NULL for currently active price rows                                                                                                         |
| `cloud`                 | STRING        | NULL     | AZURE throughout                                                                                                                             |
| `currency_code`         | STRING        | NULL     | USD throughout                                                                                                                               |
| `usage_unit`            | STRING        | NULL     | DBU, GB, HOUR, DAY, DSU                                                                                                                      |
| `default_price`         | DECIMAL(18,8) | NULL     | from `pricing.default` — standard list price per DBU/unit. DECIMAL(18,8) retains source precision and accommodates future sub-cent SKU rates |
| `pricing_json`          | STRING        | NULL     | full pricing struct serialised as JSON for auditability                                                                                      |

---

### 3. silver_cluster_current

**Source:** `system.compute.clusters`  
**Grain:** One row per cluster (current configuration version — after dedup)  
**PK:** `cluster_identifier` (natural key, NOT NULL — after dedup)  
**FK:** `workspace_identifier` → `silver_workspace_current.workspace_identifier`  
**Partition:** None  
**Load pattern:** Full Overwrite with ROW_NUMBER() Deduplication  
**Task:** 3 (parallel with Task 2)

**Purpose:**  
Metadata for all Databricks clusters. Provides cluster name, owner email, node types, autoscaling configuration, and deletion status for cost attribution and object-level analysis at gold.

**Key source findings:**

- 1,000 rows / 492 distinct cluster IDs / 399 IDs with duplicates
- `change_timestamp` is the only reliable timestamp — 0 nulls, used as dedup key
- `last_restarted_time` absent from source entirely
- `cluster_status` column absent from source
- 484 deleted clusters retained via `deleted_indicator`
- `owned_by` is the owner field → `owner_email` at silver
- `runtime_version` is the confirmed source column name (not `spark_version`)
- `driver_node_type` and `worker_node_type` are confirmed source column names

**Dedup expression:**

```sql
ROW_NUMBER() OVER (PARTITION BY cluster_id ORDER BY change_timestamp DESC) = 1
```

**Columns:**


| Column                       | Data Type          | Nullable | Notes                                       |
| ---------------------------- | ------------------ | -------- | ------------------------------------------- |
| `cluster_identifier`         | STRING             | NOT NULL | PK — from `cluster_id`                      |
| `workspace_identifier`       | STRING             | NOT NULL | FK → `silver_workspace_current`             |
| `cluster_name`               | STRING             | NULL     | from `cluster_name`                         |
| `owner_email`                | STRING             | NULL     | from `owned_by` — primary attribution field |
| `create_timestamp`           | TIMESTAMP          | NULL     | from `create_time`                          |
| `delete_timestamp`                | TIMESTAMP          | NULL     | NULL for active clusters                    |
| `driver_node_type`           | STRING             | NULL     | confirmed source column name                |
| `worker_node_type`           | STRING             | NULL     | confirmed source column name                |
| `worker_count`                | INT                | NULL     | from `worker_count`                         |
| `autoscale_min_workers`      | INT                | NULL     | from `min_autoscale_workers`                |
| `autoscale_max_workers`      | INT                | NULL     | from `max_autoscale_workers`                |
| `autotermination_minutes`    | INT                | NULL     | from `auto_termination_minutes`             |
| `elastic_disk_enabled_indicator`    | BOOLEAN            | NULL     | from `enable_elastic_disk`                  |
| `custom_tags`                | MAP<STRING,STRING> | NULL     | from `tags`                                 |
| `cluster_source`             | STRING             | NULL     | UI, JOB, API, CLONE etc.                    |
| `runtime_version`                | STRING             | NULL     | confirmed source column name                |
| `change_timestamp`                | TIMESTAMP          | NOT NULL | dedup key — 0 nulls confirmed               |
| `deleted_indicator`          | BOOLEAN            | NULL     | derived: `delete_time IS NOT NULL`          |


---

### 4. silver_warehouse_current

**Source:** `system.compute.warehouses`  
**Grain:** One row per SQL warehouse (current configuration version — after dedup)  
**PK:** `warehouse_identifier` (natural key, NOT NULL — after dedup)  
**FK:** `workspace_identifier` → `silver_workspace_current.workspace_identifier`  
**Partition:** None  
**Load pattern:** Full Overwrite 
**Task:** 4 (parallel with Task 2)

**Purpose:**  
Metadata for all SQL warehouses. Provides warehouse name, creator email, size, type, and deletion status for cost attribution at gold.

**Key source findings:**

- 30 rows / 18 distinct warehouse IDs / 12 IDs with duplicates
- `change_timestamp` is the only reliable timestamp — 0 nulls, used as dedup key
- `enable_photon`, `spot_instance_policy`, `state` absent from source as of May 2026
- `warehouse_channel` is a flat column — confirmed not a nested struct
- `min_clusters` / `max_clusters` are the confirmed source column names
- `creator_email` is the owner field — `identity_metadata.run_as` always NULL for serverless

**Dedup expression:**

```sql
ROW_NUMBER() OVER (PARTITION BY warehouse_id ORDER BY change_timestamp DESC) = 1
```

**Columns:**


| Column                 | Data Type          | Nullable | Notes                                              |
| ---------------------- | ------------------ | -------- | -------------------------------------------------- |
| `warehouse_identifier` | STRING             | NOT NULL | PK — from `warehouse_id`                           |
| `workspace_identifier` | STRING             | NOT NULL | FK → `silver_workspace_current`                    |
| `warehouse_name`       | STRING             | NULL     | from `warehouse_name`                              |
| `warehouse_type`       | STRING             | NULL     | CLASSIC, PRO, SERVERLESS                           |
| `warehouse_channel`    | STRING             | NULL     | CURRENT or PREVIEW — flat column confirmed         |
| `warehouse_size`       | STRING             | NULL     | XXSMALL through XXXLARGE                           |
| `min_cluster_count`     | INT                | NULL     | from `min_clusters` — confirmed source column name |
| `max_cluster_count`     | INT                | NULL     | from `max_clusters` — confirmed source column name |
| `auto_stop_minutes`    | INT                | NULL     | from `auto_stop_minutes`                           |
| `creator_identity`     | STRING             | NULL     | from `created_by` — primary attribution field      |
| `custom_tags`          | MAP<STRING,STRING> | NULL     | from `tags`                                        |
| `change_timestamp`          | TIMESTAMP          | NOT NULL | dedup key — 0 nulls confirmed                      |
| `delete_timestamp`          | TIMESTAMP          | NULL     | NULL for active warehouses                         |
| `deleted_indicator`    | BOOLEAN            | NULL     | derived: `delete_time IS NOT NULL`                 |


---

### 5. silver_job_current

**Source:** `system.lakeflow.jobs`  
**Grain:** One row per job (current configuration version — after dedup)  
**PK:** `job_identifier` (natural key, NOT NULL — after dedup)  
**FK:** `workspace_identifier` → `silver_workspace_current.workspace_identifier`  
**Partition:** None  
**Load pattern:** Full Overwrite with ROW_NUMBER() Deduplication  
**Task:** 5 (parallel with Task 2)

**Purpose:**  
Metadata for all Databricks jobs. Provides job name, trigger type, and deletion status for cost attribution at gold. Owner attribution for jobs is a known limitation — see open item below.

**Key source findings:**

- 1,000 rows / 489 distinct job IDs / 140 IDs with duplicates
- `change_timestamp` 0 nulls — only reliable timestamp, used as dedup key
- `create_timestamp` NULL for 941 of 1,000 rows — retained for future data
- `creator_user_name` NULL for 941 rows — not reliable as owner field
- `run_as_user_name` only 59 rows populated — not reliable as standalone owner field
- `creator_id` and `run_as` hold system IDs (e.g. `<EXAMPLE_SYSTEM_ID>`) — not emails
- 432 deleted jobs retained via `deleted_indicator`
- `format` column absent from source entirely

**Open item — no reliable email owner field (Open Item 7):**  
No column in `system.lakeflow.jobs` reliably holds an email address for the job creator or executor. `creator_email` and `run_as_email` are retained in silver for partial coverage but will result in UNRESOLVED attribution at gold for most job cost objects. Confirm whether an identity resolution step is needed before the gold notebook is written.

**Dedup expression:**

```sql
ROW_NUMBER() OVER (PARTITION BY job_id ORDER BY change_timestamp DESC) = 1
```

**Columns:**


| Column                 | Data Type          | Nullable | Notes                                        |
| ---------------------- | ------------------ | -------- | -------------------------------------------- |
| `job_identifier`       | STRING             | NOT NULL | PK — from `job_id`                           |
| `workspace_identifier` | STRING             | NOT NULL | FK → `silver_workspace_current`              |
| `job_name`             | STRING             | NULL     | from `name`                                  |
| `creator_identifier`   | STRING             | NULL     | from `creator_id` — system ID, not email     |
| `creator_user_name`        | STRING             | NULL     | from `creator_user_name` — NULL for 941 rows |
| `run_as_identifier`    | STRING             | NULL     | from `run_as` — system ID, not email         |
| `run_as_identity`      | STRING             | NULL     | from `run_as_user_name` — 59 rows populated  |
| `job_description`      | STRING             | NULL     | from `description` — 87 rows populated       |
| `trigger_type`         | STRING             | NULL     | CRON, PERIODIC etc.                          |
| `paused_indicator`     | BOOLEAN            | NULL     | from `paused`                                |
| `change_timestamp`          | TIMESTAMP          | NOT NULL | dedup key — 0 nulls confirmed                |
| `create_timestamp`          | TIMESTAMP          | NULL     | NULL for 941 rows — retained for future data |
| `delete_timestamp`          | TIMESTAMP          | NULL     | NULL for active jobs                         |
| `custom_tags`          | MAP<STRING,STRING> | NULL     | from `tags`                                  |
| `deleted_indicator`    | BOOLEAN            | NULL     | derived: `delete_time IS NOT NULL`           |


---

### 6. silver_workspace_current

**Source:** `system.access.workspaces_latest`  
**Grain:** One row per workspace (current state only)  
**PK:** `workspace_identifier` (natural key, NOT NULL)  
**FK:** None — this is the referenced table  
**Partition:** None  
**Load pattern:** Full Overwrite  
**Task:** 6 (parallel with Task 2)

**Purpose:**  
Workspace reference table and the FK anchor for all other silver metadata tables. Provides workspace name, URL, and status for labelling and filtering at gold. The `_latest` suffix in the source table name guarantees only current state is delivered — no dedup needed, no timestamp guard needed.

**Key source findings:**

- `workspaces_latest` delivers only currently active workspaces — confirmed 2 rows (Prod and Dev, both RUNNING)
- Decommissioned workspaces are absent from source entirely — their labels will be null at query time
- 17 distinct `workspace_id` values in billing history — only 2 resolvable. 15 decommissioned, metadata permanently unavailable
- MERGE Standard Upsert — no DELETE clause. Rows never removed from silver even when absent from source

**MERGE behaviour:**

```sql
WHEN MATCHED     → UPDATE workspace_text, workspace_url, workspace_status
WHEN NOT MATCHED → INSERT new workspace row
-- No WHEN NOT MATCHED BY SOURCE clause — rows never deleted
```

**Why Full Overwrite (not MERGE):**

`MERGE INTO IDENTIFIER(:prefix || '...')` is not supported in Databricks SQL
notebooks — the IDENTIFIER clause does not accept session variables in MERGE
context (SQLSTATE: 42601). `system.access.workspaces_latest` is a latest-state
view — Full Overwrite is the correct and simpler pattern. If a workspace
disappears from source it is removed from silver on the next run, which is
the correct behaviour for a `_current` table.

**Columns:**


| Column                         | Data Type | Nullable | Notes                                                  |
| ------------------------------ | --------- | -------- | ------------------------------------------------------ |
| `workspace_identifier`         | STRING    | NOT NULL | PK — from `workspace_id`                               |
| `account_identifier`           | STRING    | NOT NULL | from `account_id`                                      |
| `workspace_name`               | STRING    | NULL     | from `workspace_name` — NULL for decommissioned        |
| `workspace_url`                | STRING    | NULL     | access URL                                             |
| `workspace_creation_timestamp` | TIMESTAMP | NULL     | from `create_time`                                     |
| `workspace_status`             | STRING    | NULL     | RUNNING, PROVISIONING, FAILED, BANNED, NOT_PROVISIONED |


---

### 7. silver_pipeline_current

**Source:** `system.lakeflow.pipelines`  
**Grain:** One row per DLT pipeline (current configuration version — after dedup)  
**PK:** `pipeline_identifier` (natural key, NOT NULL — after dedup)  
**FK:** `workspace_identifier` → `silver_workspace_current.workspace_identifier`  
**Partition:** None  
**Load pattern:** Full Overwrite with ROW_NUMBER() Deduplication  
**Task:** 7 (parallel with Task 2)

**Purpose:**  
Metadata for all DLT pipelines. Provides pipeline name, creator email, pipeline type, and deletion status for cost attribution at gold. Best owner coverage of any metadata table — `creator_email` 100% populated.

**Key source findings:**

- 1,000 rows / 402 distinct pipeline IDs / 343 IDs with duplicates (85% duplicate rate — highest of all metadata tables)
- `change_timestamp` 0 nulls — the only reliable timestamp, used as dedup key
- `create_timestamp` NULL for all 1,000 rows — retained for future data
- `creator_email` 100% populated with email addresses — most reliable owner field
- `run_as_email` 99.7% populated with email addresses
- 330 deleted pipelines retained via `deleted_indicator`
- `storage`, `catalog`, `schema` absent from source as of May 2026
- `settings` and `configuration` structs serialised as JSON for auditability
- Pipeline types: 975 MATERIALIZED_VIEW, 14 STREAMING_TABLE, 7 ETL_PIPELINE, 2 INGESTION_PIPELINE, 2 INGESTION_GATEWAY

**Dedup expression:**

```sql
ROW_NUMBER() OVER (PARTITION BY pipeline_id ORDER BY change_timestamp DESC) = 1
```

**Columns:**


| Column                 | Data Type          | Nullable | Notes                                                              |
| ---------------------- | ------------------ | -------- | ------------------------------------------------------------------ |
| `pipeline_identifier`  | STRING             | NOT NULL | PK — from `pipeline_id`                                            |
| `workspace_identifier` | STRING             | NOT NULL | FK → `silver_workspace_current`                                    |
| `pipeline_name`        | STRING             | NULL     | from `name`                                                        |
| `pipeline_type`        | STRING             | NULL     | MATERIALIZED_VIEW, STREAMING_TABLE, ETL_PIPELINE etc.              |
| `creator_email`        | STRING             | NULL     | from `created_by` — 100% populated                                 |
| `run_as_email`         | STRING             | NULL     | from `run_as` — 99.7% populated                                    |
| `custom_tags`          | MAP<STRING,STRING> | NULL     | from `tags`                                                        |
| `settings_json`        | STRING             | NULL     | from `settings` struct — serialised as JSON                        |
| `configuration_json`   | STRING             | NULL     | from `configuration` struct — serialised as JSON                   |
| `change_timestamp`          | TIMESTAMP          | NOT NULL | dedup key — 0 nulls confirmed                                      |
| `create_timestamp`          | TIMESTAMP          | NULL     | NULL throughout in current live extract — retained for future data |
| `delete_timestamp`          | TIMESTAMP          | NULL     | NULL for active pipelines                                          |
| `deleted_indicator`    | BOOLEAN            | NULL     | derived: `delete_time IS NOT NULL`                                 |


---

### 8. silver_served_entity_current

**Source:** `system.serving.served_entities`  
**Grain:** One row per model serving endpoint entity (current configuration version — after dedup)  
**PK:** `served_entity_identifier` (natural key, NOT NULL — after dedup)  
**FK:** `workspace_identifier` → `silver_workspace_current.workspace_identifier`  
**Partition:** None  
**Load pattern:** Full Overwrite with ROW_NUMBER() Deduplication  
**Task:** 8 (parallel with Task 2)

**Purpose:**  
Metadata for all model serving endpoint entities. Provides endpoint name, entity type, creator email, and deletion status for cost attribution at gold. FOUNDATION_MODEL endpoints are Databricks-managed — their `creator_email` is `System-User` and will return UNRESOLVED at gold. This is expected behaviour, not a data quality issue.

**Key source findings:**

- 5 rows / 5 distinct IDs in current live extract (8 rows with 3 duplicates confirmed in earlier extract)
- `change_timestamp` 0 nulls — used as dedup key
- 3 entities deleted (`endpoint_delete_time` populated) — retained via `deleted_indicator`
- 2 FOUNDATION_MODEL entities active — `created_by = System-User` — UNRESOLVED at gold
- `external_model_config` and `feature_spec_config` NULL throughout — not retained
- `endpoint_delete_time` from source renamed to `delete_timestamp` at silver

**Dedup expression:**

```sql
ROW_NUMBER() OVER (PARTITION BY served_entity_id ORDER BY change_timestamp DESC) = 1
```

**Columns:**


| Column                         | Data Type | Nullable | Notes                                                      |
| ------------------------------ | --------- | -------- | ---------------------------------------------------------- |
| `served_entity_identifier`     | STRING    | NOT NULL | PK — from `served_entity_id`                               |
| `workspace_identifier`         | STRING    | NOT NULL | FK → `silver_workspace_current`                            |
| `endpoint_identifier`          | STRING    | NULL     | from `endpoint_id`                                         |
| `endpoint_name`                | STRING    | NULL     | from `endpoint_name`                                       |
| `served_entity_name`           | STRING    | NULL     | from `served_entity_name`                                  |
| `entity_type`                  | STRING    | NULL     | CUSTOM_MODEL or FOUNDATION_MODEL                           |
| `entity_name`                  | STRING    | NULL     | from `entity_name`                                         |
| `entity_version`               | STRING    | NULL     | STRING to accommodate non-numeric versions                 |
| `endpoint_config_version`      | INT       | NULL     | differentiates duplicate config rows                       |
| `task`                         | STRING    | NULL     | llm/v1/chat or agent/v1/chat                               |
| `creator_identity`                | STRING    | NULL     | from `created_by` — System-User for FOUNDATION_MODEL       |
| `custom_model_config_json`     | STRING    | NULL     | from `custom_model_config` struct — serialised as JSON     |
| `foundation_model_config_json` | STRING    | NULL     | from `foundation_model_config` struct — serialised as JSON |
| `change_timestamp`                  | TIMESTAMP | NOT NULL | dedup key — 0 nulls confirmed                              |
| `delete_timestamp`                  | TIMESTAMP | NULL     | from `endpoint_delete_time` — renamed at silver            |
| `deleted_indicator`            | BOOLEAN   | NULL     | derived: `endpoint_delete_time IS NOT NULL`                |


---

### 9. silver_query_history

**Source:** `system.query.history`
**Grain:** One row per query execution — all execution statuses retained (`FINISHED`, `FAILED`, `CANCELED`)
**PK:** `query_identifier` (NOT NULL) — from `statement_id`
**FK:** `workspace_identifier` → `silver_workspace_current.workspace_identifier`
**Partition:** `query_start_hour` (derived as `DATE_TRUNC('HOUR', start_timestamp)`)
**Load pattern:** Append with Watermark on `start_timestamp`
**Task:** 9 (parallel — no cross-dependency with other silver tasks)

**Purpose:**
Central query audit table at silver. Every Databricks SQL query execution since February 2026 lives here — 1,852,210 rows growing daily. Records are immutable once written. All execution statuses are retained at silver (`FINISHED`, `FAILED`, `CANCELED`) — status filtering to `FINISHED` only is applied at gold. Two derived columns are added at load time: `query_start_hour` and `query_start_date`. Two source columns are deliberately excluded for governance reasons: `statement_text` and `error_message`.

**Key source findings:**

- 1,852,210 rows loaded in dev — all statuses present
- Records are immutable — Append with Watermark on `start_timestamp` is correct
- `query_identifier` (from `statement_id`) is 100% unique — confirmed as natural PK
- `total_task_duration_ms` is the primary attribution metric — 0.37% null rate, reflects true parallel compute across all CPU cores
- `execution_duration_ms` has 9.69% null rate — do NOT use for cost attribution
- `end_timestamp` is 0.004% null (73 rows from non-Claude tools) — confirmed acceptable
- Two client application strings identify Claude MCP queries: `Databricks SQL MCP` (Feb 2026 → present) and `DatabricksDbsqlMcp` (Feb 2026 → Apr 2026, legacy). No fuzzy matching required — these are unambiguous identifiers
- Claude identification is handled in the dashboard layer by filtering `client_application` directly — no derived boolean column in the pipeline

**Execution status profiling (Claude MCP queries):**

| Status   | Count  | % of Total | Total Task Seconds | % of Task Seconds |
| -------- | ------ | ---------- | ------------------ | ----------------- |
| FINISHED | 10,138 | 89.80%     | 93,761.9s          | 99.9898%          |
| FAILED   | 1,151  | 10.20%     | 9.6s               | 0.0102%           |
| CANCELED | 0      | 0.00%      | 0s                 | 0%                |

**Duration column reference:**

| Column                           | What It Measures                        | Null % | Use                                          |
| -------------------------------- | --------------------------------------- | ------ | -------------------------------------------- |
| `total_duration_ms`              | Wall-clock — all phases                 | 0.00%  | Reference only                               |
| `waiting_for_compute_duration_ms`| Warehouse cold start wait               | 0.33%  | Warehouse health                             |
| `waiting_at_capacity_duration_ms`| Queue wait — warehouse full             | 0.33%  | Capacity indicator                           |
| `compilation_duration_ms`        | Parse, plan, optimize                   | 9.64%  | Query complexity                             |
| `execution_duration_ms`          | Execution wall-clock                    | 9.69%  | Reference — do NOT use for attribution       |
| `total_task_duration_ms`         | Sum of all parallel task CPU time       | 0.37%  | **PRIMARY attribution metric**               |
| `result_fetch_duration_ms`       | Result transfer to client               | 0.38%  | Result size indicator                        |

**Column exclusions — governance:**

- `statement_text` — may contain sensitive business data, PII, or proprietary query logic. Databricks redacts with customer-managed keys. Excluded deliberately.
- `error_message` — may contain sensitive data. Failure tracking is handled via `execution_status` only. Databricks redacts with customer-managed keys. Excluded deliberately.

**Columns:**

| Column                             | Type      | Nullable | Notes                                                              |
| ---------------------------------- | --------- | -------- | ------------------------------------------------------------------ |
| `query_identifier`                 | STRING    | NOT NULL | PK — from `statement_id`                                           |
| `workspace_identifier`             | STRING    | NOT NULL | FK → `silver_workspace_current`                                    |
| `executed_by_identity`             | STRING    | NULL     | Primary user attribution field — from `executed_by`               |
| `warehouse_identifier`             | STRING    | NULL     | Join key to `gold_fact_usage` and `silver_warehouse_current`       |
| `client_application`               | STRING    | NULL     | Dashboard filters on this column to identify Claude queries        |
| `client_driver`                    | STRING    | NULL     | `DatabricksSqlExecApi, 2.0` for all Claude queries — audit field   |
| `execution_status`                 | STRING    | NULL     | FINISHED, FAILED, CANCELED — all retained at silver               |
| `statement_type`                   | STRING    | NULL     | SELECT, DESCRIBE, etc.                                             |
| `result_cache_hit_indicator`       | BOOLEAN   | NULL     | TRUE = near-zero compute consumed                                  |
| `start_timestamp`                  | TIMESTAMP | NOT NULL | Watermark column                                                   |
| `end_timestamp`                    | TIMESTAMP | NULL     | 0.004% null — 73 rows from non-Claude tools, confirmed acceptable  |
| `query_start_hour`                 | TIMESTAMP | NOT NULL | Partition key — derived: `DATE_TRUNC('HOUR', start_timestamp)`     |
| `query_start_date`                 | DATE      | NOT NULL | Derived: `CAST(start_timestamp AS DATE)` — join key to `gold_fact_usage` |
| `total_duration_ms`                | BIGINT    | NULL     | Wall-clock — reference only                                        |
| `waiting_for_compute_duration_ms`  | BIGINT    | NULL     | 0.33% null                                                         |
| `waiting_at_capacity_duration_ms`  | BIGINT    | NULL     | 0.33% null                                                         |
| `compilation_duration_ms`          | BIGINT    | NULL     | 9.64% null                                                         |
| `execution_duration_ms`            | BIGINT    | NULL     | 9.69% null — do NOT use for attribution                            |
| `total_task_duration_ms`           | BIGINT    | NULL     | **PRIMARY attribution metric** — 0.37% null                        |
| `result_fetch_duration_ms`         | BIGINT    | NULL     | 0.38% null                                                         |
| `read_rows`                        | BIGINT    | NULL     | Query complexity indicator                                         |
| `produced_rows`                    | BIGINT    | NULL     | Result set size                                                     |
| `read_bytes`                       | BIGINT    | NULL     | Data scan volume                                                    |
| `session_identifier`               | STRING    | NULL     | Audit — equals `query_identifier` throughout Claude MCP            |

---

## Gold Layer Overview

The gold layer follows the star schema design per the Silver + Gold Modeling Reference. Four materialized tables, one standalone fact table, and two SQL views.

| Object                          | Type      | Load Pattern                          | Partition        |
| ------------------------------- | --------- | ------------------------------------- | ---------------- |
| `gold_dim_workspace`            | Dimension | Full Overwrite                        | None             |
| `gold_dim_sku`                  | Dimension | Full Overwrite                        | None             |
| `gold_dim_object`               | Dimension | Full Overwrite                        | None             |
| `gold_fact_usage`               | Fact      | DELETE + INSERT (Partition-selective) | `usage_hour`     |
| `gold_query_history`            | Fact      | DELETE + INSERT (Partition-selective) | `query_start_hour` |
| `gold_top_cost_objects_current` | View      | No load — SQL view                    | —                |
| `gold_daily_spend_trend`        | View      | No load — SQL view                    | —                |

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
| `workspace_name`       | STRING          | Display label. NULL for decommissioned workspaces absent from source |
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
| `object_name`        | STRING          | Human-readable label from silver metadata. NULL for deleted objects                                                                                   |
| `owner_identity`     | STRING          | Resolved identity from COALESCE chain. Email for human owners. Service principal or system identifier for non-human identities. NULL where UNRESOLVED |
| `attribution_method` | STRING NOT NULL | How owner was resolved — `executed_by_identity`, `creator_email`, `owner_email`, `UNRESOLVED`                                                         |
| `workspace_sk`       | BIGINT NOT NULL | FK → `gold_dim_workspace.workspace_sk`                                                                                                                |
| `last_activity_date` | DATE            | MAX(`usage_date`) across all billing records for this object. Recalculated on every daily Full Overwrite run                                          |
| `idle_day_count`     | INT             | `DATEDIFF(CURRENT_DATE(), last_activity_date)`. Recalculated on every daily Full Overwrite run                                                        |
| `deleted_indicator`  | BOOLEAN         | TRUE when object identifier absent from all silver metadata tables after dedup                                                                        |


---

### 12. gold_fact_usage — Partition / Predicate-based Overwrite

**Source:** `silver_usage_history`  
**Load Pattern:** DELETE + INSERT (Partition-selective)`  
**Trigger:** Daily  
**Type:** Fact  
**Grain:** One row per `workspace_sk × object_sk × sku_sk × usage_hour`  
**PK:** `workspace_sk + object_sk + sku_sk + usage_hour` (composite)  
**Partition:** `usage_hour`

Central hourly spend fact table. Carries all additive measures per Silver + Gold Modeling Reference — no descriptive attributes. Object names, owner identity, and workspace labels are resolved by joining to dimension tables at query time.

**Why DELETE + INSERT (not Full Overwrite)**:
Full Overwrite rewrites the entire table on every run. As
silver_usage_history grows to 2+ years of hourly billing data,
Full Overwrite becomes expensive daily. DELETE + INSERT only touches
partitions in the daily watermark window (typically 24-48 hours)
leaving all historical partitions untouched. This is equivalent to
dynamic partition overwrite but implemented in two explicit DML steps
since spark.sql.sources.partitionOverwriteMode is not available on
Serverless Warehouse (SQLSTATE: 42K0I).

**Why not Partition Overwrite (original design)**:
REPLACE WHERE with subquery not supported (SQLSTATE: 0A000).
spark.sql.sources.partitionOverwriteMode not available on Serverless
Warehouse (SQLSTATE: 42K0I).

Load window gap:
Between DELETE completing and INSERT completing, affected hours have
zero rows in gold. Dashboard queries landing in this window get
incomplete results for those hours. Acceptable for a daily batch
pipeline — schedule dashboards to refresh after pipeline completes.

Watermark: MAX(usage_hour) from gold_fact_usage.
First run: table empty — watermark = 1900-01-01 — DELETE finds
nothing — INSERT loads all silver. Safe.

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
### 15. gold_query_history — DELETE + INSERT (Partition-selective)

**Source:** `silver_query_history` LEFT JOIN `silver_warehouse_current` LEFT JOIN `silver_workspace_current`
**Load Pattern:** DELETE + INSERT (Partition-selective on `query_start_hour`)
**Trigger:** Daily after `silver_query_history`
**Type:** Fact
**Grain:** One row per FINISHED query execution
**PK:** `query_identifier` (NOT NULL)
**Partition:** `query_start_hour`

**Purpose:**
Standalone query history fact table. Holds every FINISHED Databricks SQL query execution with denormalized warehouse and workspace names to eliminate joins in the dashboard layer. The primary consumer is the Power BI Claude Cost Analytics dashboard, which applies the pro-rata attribution formula against this table and `gold_fact_usage` to estimate Claude's share of warehouse compute cost. No attribution logic lives in the pipeline — the pipeline delivers the raw ingredients, the dashboard applies the formula.

**Why DELETE + INSERT (not Full Overwrite):**
At 1,783,948 rows and growing daily, Full Overwrite rewrites the entire table on every run. DELETE + INSERT only touches partitions in the daily watermark window (typically 24–48 hours), leaving all historical partitions untouched. Identical pattern to `gold_fact_usage` — same constraint applies: `spark.sql.sources.partitionOverwriteMode` is not available on Serverless Warehouse (SQLSTATE: 42K0I).

**Why FINISHED only:**
FAILED queries consume 0.0102% of total task seconds (9.6s out of 93,761.9s) — confirmed negligible by profiling. CANCELED = 0 observed across all Claude MCP queries. Gold applies a whitelist filter: any new or unknown execution status is automatically excluded until explicitly evaluated.

**Future status maintenance:**
- If CANCELED queries appear — profile `total_task_duration_ms` before including. Suggested future filter: `WHERE execution_status IN ('FINISHED', 'CANCELED')`
- If Databricks introduces new statuses (TIMED_OUT, PARTIAL) — evaluate compute impact before including
- Any status filter change requires a full reload of `gold_query_history` from silver — set `initial_full_load = True`

**Claude query identification:**
No derived boolean column in the pipeline. The dashboard identifies Claude queries by filtering `client_application` directly:

```sql
WHERE client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
```

This approach is transparent, maintainable, and consistent with the design principle that business logic belongs in the dashboard layer. Adding new client strings in future requires only a dashboard change — no pipeline change.

**Attribution formula (applied in Power BI DAX, not in pipeline):**

Daily grain is critical — monthly grain inflates results on shared warehouses with volatile daily Claude shares. Confirmed during methodology review: monthly grain produced $904 vs correct daily grain of $462.

**Dev validation results:**
- 1,783,948 rows loaded — FINISHED only confirmed
- Silver → gold row difference = 0
- Zero duplicates on `query_identifier` after full run and after re-run
- Attribution formula validated at $462.02 (Feb 11 – Jun 11 2026)

**Columns:**

| Column                             | Type      | Nullable | Notes                                                                        |
| ---------------------------------- | --------- | -------- | ---------------------------------------------------------------------------- |
| `query_identifier`                 | STRING    | NOT NULL | PK — from `statement_id` via silver                                          |
| `workspace_identifier`             | STRING    | NOT NULL | FK → `gold_dim_workspace` via `workspace_sk`                                 |
| `workspace_name`                   | STRING    | NULL     | Denormalized from `silver_workspace_current` — eliminates join in dashboard  |
| `executed_by_identity`             | STRING    | NULL     | Primary user attribution field                                               |
| `warehouse_identifier`             | STRING    | NULL     | Join key to `gold_fact_usage` for attribution formula                        |
| `warehouse_name`                   | STRING    | NULL     | Denormalized — 11.72% null for deleted/decommissioned warehouses. Expected and documented |
| `client_application`               | STRING    | NULL     | Dashboard filters on this column directly to identify Claude queries         |
| `client_driver`                    | STRING    | NULL     | `DatabricksSqlExecApi, 2.0` for all Claude queries — audit field             |
| `execution_status`                 | STRING    | NOT NULL | Always `FINISHED` at gold                                                    |
| `statement_type`                   | STRING    | NULL     | SELECT, DESCRIBE, etc.                                                       |
| `result_cache_hit_indicator`       | BOOLEAN   | NULL     | TRUE = near-zero compute consumed — relevant for attribution accuracy        |
| `start_timestamp`                  | TIMESTAMP | NOT NULL | UTC                                                                          |
| `end_timestamp`                    | TIMESTAMP | NULL     | 0.004% null — 73 rows from non-Claude tools, zero impact on attribution      |
| `query_start_hour`                 | TIMESTAMP | NOT NULL | Partition key                                                                |
| `query_start_date`                 | DATE      | NOT NULL | Join key to `gold_fact_usage` for daily attribution formula                  |
| `total_duration_ms`                | BIGINT    | NULL     | Reference only                                                               |
| `waiting_for_compute_duration_ms`  | BIGINT    | NULL     | 0.33% null                                                                   |
| `waiting_at_capacity_duration_ms`  | BIGINT    | NULL     | 0.33% null                                                                   |
| `compilation_duration_ms`          | BIGINT    | NULL     | 9.64% null                                                                   |
| `execution_duration_ms`            | BIGINT    | NULL     | 9.69% null — do NOT use for attribution                                      |
| `total_task_duration_ms`           | BIGINT    | NULL     | **PRIMARY attribution metric** — 0.37% null                                  |
| `result_fetch_duration_ms`         | BIGINT    | NULL     | 0.38% null                                                                   |
| `read_rows`                        | BIGINT    | NULL     | Query complexity indicator                                                   |
| `produced_rows`                    | BIGINT    | NULL     | Result set size                                                              |
| `read_bytes`                       | BIGINT    | NULL     | Data scan volume                                                             |
| `session_identifier`               | STRING    | NULL     | Audit — equals `query_identifier` throughout Claude MCP                      |

---
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


gold_query_history  (Partition / query_start_hour)
───────────────────────────────────────────────────────────────────
query_identifier          (PK)
workspace_identifier      (NK — joins to gold_dim_workspace)
workspace_name            (denormalized)
executed_by_identity
warehouse_identifier      (join key to gold_fact_usage for attribution)
warehouse_name            (denormalized — 11.72% null for deleted warehouses)
client_application        (dashboard filters on this column for Claude queries)
client_driver
execution_status          (always FINISHED at gold)
statement_type
result_cache_hit_indicator
start_timestamp
end_timestamp
query_start_hour          (partition key)
query_start_date          (join key to gold_fact_usage for daily attribution formula)
total_duration_ms
waiting_for_compute_duration_ms
waiting_at_capacity_duration_ms
compilation_duration_ms
execution_duration_ms
total_task_duration_ms    (PRIMARY attribution metric)
result_fetch_duration_ms
read_rows
produced_rows
read_bytes
session_identifier

Note: gold_query_history is a standalone fact table. It does not join into the
billing star schema above. It joins to gold_fact_usage at the dashboard layer
via warehouse_identifier + query_start_date to apply the pro-rata attribution
formula for Claude cost estimation.
```
## Open Items

| # | Item | Detail | Owner |
| --- | --- | --- | --- |
| 1 | `silver_usage_history` watermark assumption — CLOSED | Correction rows (RETRACTION / RESTATEMENT) are possible per Databricks documentation but 0 observed across 268,127 rows in EDA. A strict forward-only watermark could miss correction rows if the corrected timestamp falls behind the current watermark position. Risk accepted and documented. Reopen if correction rows are observed in future. | Closed |
| 2 | `product_family` mapping for `gold_dim_sku` | Taxonomy needs reviewer sign-off before `gold_dim_sku` notebook. Live list_prices data confirms broader categories — Compute, SQL Analytics, Serving, Apps, Clean Rooms, DLT, Model Training, Egress, Storage, Private Connectivity. | Data + Automation Team |
| 3 | `silver_workspace_current` — null labels for 15 workspaces | EDA confirmed 17 distinct `workspace_id` values in `system.billing.usage`. `workspaces_latest` returns only 2 active workspaces. 15 decommissioned workspace IDs have no metadata available — their workspace label will be null at query time. Source limitation — no pipeline action required. | Documented — no action |
| 4 | `silver_pipeline_current` — `create_time` NULL throughout | `create_time` is NULL for all 1,000 rows in the current live extract. Column retained for future data. If Databricks starts populating `create_time`, no schema change is needed. | Documented |
| 5 | `enable_photon` on `silver_warehouse_current` | `enable_photon` absent from live source as of May 2026. Photon enablement has billing implications. Revisit if column appears in future extracts. | Documented |
| 6 | All load pattern decisions + 2 views sign-off | Full review and sign-off required before Child 3 notebook work begins. | Data + Automation Team |
| 7 | `silver_job_current` owner attribution | No reliable email owner field in `system.lakeflow.jobs`. `creator_user_name` NULL for 94% of rows. `creator_id` and `run_as` hold system IDs not emails. Job cost objects will return UNRESOLVED at gold for most rows. Confirm whether identity resolution step needed before gold notebook is written. | Data + Automation Team |

---
## Design Decisions

| Decision | Standard default | Chosen approach | Rationale |
| --- | --- | --- | --- |
| All `_current` metadata tables | MERGE Conditional (Timestamp-Guarded) | Full Overwrite with ROW_NUMBER() Deduplication | Live source extracts confirmed assumed timestamp columns (`last_restarted_time`, `last_modified_time`) do not exist. `change_time` is the only reliable timestamp across all metadata tables. Full rebuild eliminates stale rows without a MERGE guard. |
| `deleted_indicator` naming | `is_deleted` | `deleted_indicator` | Per the internal data naming standard — `_indicator` suffix is the correct representation for boolean values. |
| Table suffix convention | No suffix | `_history` / `_current` | Per Unity Catalog naming standard — suffix communicates data state instantly. `_history` for accumulating tables, `_current` for current-state tables. |
| `silver_list_prices_history` — price field | `default_unit_price` | `pricing.default` → `default_price` | `pricing.default` is the published standard list price per Databricks documentation and the officially endorsed field for cost calculation — confirmed from Databricks sample query: `usage_quantity * list_prices.pricing.default as list_cost`. Promotional rates not applied — deliberate decision accepted and documented. |
| `silver_job_current` — owner field | Single email column | Three identity columns retained | No single column is reliable. `creator_email` (94% null), `run_as_identity` (mixed), `creator_identifier` and `run_as_identifier` (system IDs) all retained. Owner resolution handled at gold via COALESCE chain. |
| Identity field naming (`_email` vs `_identity`) | `_email` suffix on all identity fields | `_email` only where 100% email confirmed | Live source extract confirmed `warehouse_current.created_by` and `served_entity_current.created_by` contain mixed values (emails, numeric IDs, System-User). These map to `creator_identity`. `cluster_current.owned_by`, `pipeline_current.created_by`, and `job_current.creator_user_name` are 100% email — retain `_email` suffix. |
| `gold_dim_object` | INSERT OVERWRITE | Full Overwrite | No ownership history tracking required for this pipeline — current owner only. Historical ownership attribution is out of scope. SCD Type 2 columns (`valid_from`, `valid_to`, `active_indicator`) removed. |
| `gold_dim_workspace` — `is_active` column | `is_active` boolean | Column removed | `workspace_status` already provides active/inactive state directly. Derived boolean flag adds no value. |
| `gold_dim_sku` | SKU flat on fact | Dedicated dimension | Product family is a derived business grouping that does not exist in the source. Belongs in a dimension, not hardcoded in every query. Current price surfaced here without joining back to silver. |
| `gold_fact_usage` — grain | Daily | Hourly (`usage_hour`) | Source is hourly grain per Databricks documentation — each billing row represents up to one hour of compute. Gold retains hourly grain. Daily aggregation and rolling averages handled in `gold_daily_spend_trend` view. |
| `gold_fact_usage` — `object_sk` on grain | No object at fact grain | `object_sk` included | Enables direct join to `gold_dim_object` for object name, owner identity, idle status, and deletion flag at query time. |
| `gold_fact_usage` — rolling averages | Pre-stored columns | `gold_daily_spend_trend` view | Pre-storing rolling averages forces Full Overwrite (window spans all partitions). View computes on demand at no storage cost and also handles daily aggregation from hourly grain. |
| `gold_fact_usage` — tag columns | Tag dimension table | Flat columns on fact | Unpivoting 3 tag keys creates 3× row fan-out and complicates the grain. Low-cardinality flat columns filter efficiently at query time. |
| `gold_top_cost_objects_current` | Aggregation table | SQL view — no storage | View over `gold_fact_usage` and `gold_dim_object` is always current and requires no job task. |
| `silver_usage_history` — cost derivation | Cost at gold view | `usage_cost` at silver load time | `silver_usage_history` joins to `silver_list_prices_history` at load time and computes `usage_cost = usage_quantity × pricing.default` per billing record. |
| `gold_daily_spend_trend` — daily cost | Pre-stored on fact | Derived in view | `daily_cost = SUM(usage_cost)` aggregated from hourly fact grain to daily in the view. Keeps fact table at hourly grain while providing daily totals for reporting. |
| `silver_query_history` — governance exclusions | Retain all source columns | Exclude `statement_text` and `error_message` | Both columns may contain sensitive business data or PII. Databricks redacts with customer-managed keys. Failure tracking handled via `execution_status` only. Excluded deliberately — not a pipeline gap. |
| `gold_query_history` — status filter | All statuses | FINISHED only | FAILED = 0.0102% of total task seconds (9.6s out of 93,761.9s) — confirmed negligible by profiling. CANCELED = 0 observed. Whitelist approach — any new status is automatically excluded until explicitly evaluated. |
| `gold_query_history` — load pattern | Full Overwrite | DELETE + INSERT (partition-selective on `query_start_hour`) | 1,783,948 rows and growing daily. Partition-selective pattern is efficient — only touches daily watermark window. Identical constraint to `gold_fact_usage`: `spark.sql.sources.partitionOverwriteMode` not available on Serverless Warehouse (SQLSTATE: 42K0I). |
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
- Unity Catalog Policy and Naming Standards — Process Standards
- internal data naming standard v6.0 — Process Standards
