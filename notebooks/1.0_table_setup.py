# Databricks notebook source
# MAGIC %md
# MAGIC # 1.0 Table Setup — Databricks Cost Analytics
# MAGIC
# MAGIC Creates all silver and gold Delta tables for the Databricks Cost Analytics pipeline.
# MAGIC
# MAGIC **Target:** `data_automation.databricks_analytics` (prefixed with `dev_` in development)
# MAGIC
# MAGIC | Table | Layer | Grain |
# MAGIC | --- | --- | --- |
# MAGIC | `silver_workspace_current` | Silver | One row per workspace (current state) |
# MAGIC | `silver_list_prices_history` | Silver | One row per SKU per price effective period |
# MAGIC | `silver_usage_history` | Silver | One row per billing usage record |
# MAGIC | `silver_cluster_current` | Silver | One row per cluster (current configuration) |
# MAGIC | `silver_warehouse_current` | Silver | One row per SQL warehouse (current configuration) |
# MAGIC | `silver_job_current` | Silver | One row per job (current configuration) |
# MAGIC | `silver_pipeline_current` | Silver | One row per DLT pipeline (current configuration) |
# MAGIC | `silver_served_entity_current` | Silver | One row per model serving endpoint entity (current configuration) |
# MAGIC | `silver_query_history` | Silver | One row per query execution — all statuses retained |
# MAGIC | `gold_query_history`   | Gold   | One row per FINISHED query execution               |
# MAGIC | `gold_dim_workspace` | Gold | One row per workspace |
# MAGIC | `gold_dim_sku` | Gold | One row per SKU |
# MAGIC | `gold_dim_object` | Gold | One row per billable object (current state) |
# MAGIC | `gold_fact_usage` | Gold | One row per workspace × object × SKU × usage_hour |
# MAGIC
# MAGIC DDL runs only when `initial_full_load = True`. Day-to-day loads should leave it `False`.
# MAGIC
# MAGIC **Views** (`gold_top_cost_objects_current`, `gold_daily_spend_trend`) are created in `3.0_gold_databricks_analytics.sql` — not here.

# COMMAND ----------

# DBTITLE 1,imports
# MAGIC %run ./init_libraries

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 3 - Widgets

# COMMAND ----------

dbutils.widgets.text("environment",       "dev")
dbutils.widgets.text("initial_full_load", "False")
dbutils.widgets.text("verbose",           "False")

environment       = dbutils.widgets.get("environment").strip().lower()
initial_full_load = dbutils.widgets.get("initial_full_load").strip().lower() == "true"
verbose           = dbutils.widgets.get("verbose").strip().lower() == "true"
prefix            = "dev_" if environment == "dev" else ""

CATALOG = "data_automation"
SCHEMA  = "databricks_analytics"
OWNER   = "data_science"

target_catalog = f"{prefix}{CATALOG}"

print(f"  environment       = {environment}")
print(f"  initial_full_load = {initial_full_load}")
print(f"  verbose           = {verbose}")
print(f"  target catalog    = {target_catalog}")
print(f"  target schema     = {SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 4 - Guard

# COMMAND ----------

assert environment in ("dev", "prod"), f"Invalid environment: '{environment}'. Must be 'dev' or 'prod'."

if not initial_full_load:
    dbutils.notebook.exit("initial_full_load is False — skipping table setup.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 5 - Column comments (data dictionary)
# MAGIC Single `DD` dict keyed by silver/gold column name.
# MAGIC Sourced from approved table_designs.md — source of truth.

# COMMAND ----------

# ── Cell 5 — Column comments (data dictionary) ────────────────────────────────
# Keyed by (table_name, column_name) tuples to prevent silent key collisions
# across tables that share column names but carry different semantics.
# create_table() filters to the matching table before applying comments.

DD = {

    # ── silver_workspace_current ──────────────────────────────────────────────
    ("silver_workspace_current", "workspace_identifier"):         "Unique identifier of the Databricks workspace. Primary key. NOT NULL.",
    ("silver_workspace_current", "account_identifier"):           "Identifier of the Databricks account that owns this workspace. NOT NULL.",
    ("silver_workspace_current", "workspace_name"):               "Display name of the Databricks workspace as configured. NULL for decommissioned workspaces absent from source.",
    ("silver_workspace_current", "workspace_url"):                "Full URL of the Databricks workspace.",
    ("silver_workspace_current", "workspace_creation_timestamp"): "Timestamp when the Databricks workspace was provisioned.",
    ("silver_workspace_current", "workspace_status"):             "Current operational status of this workspace. RUNNING, PROVISIONING, FAILED, BANNED, NOT_PROVISIONED.",

    # ── silver_list_prices_history ────────────────────────────────────────────
    ("silver_list_prices_history", "sku_name"):               "Databricks SKU code identifying the product and compute type. Primary key component. NOT NULL.",
    ("silver_list_prices_history", "price_start_timestamp"):  "Timestamp from which this list price became effective. Primary key component. NOT NULL.",
    ("silver_list_prices_history", "price_end_timestamp"):    "Timestamp when this list price was superseded. NULL for the currently active price row.",
    ("silver_list_prices_history", "cloud"):                  "Cloud provider on which the price applies. AZURE throughout the account.",
    ("silver_list_prices_history", "currency_code"):          "ISO 4217 currency code for the price value. USD throughout the the client organization account.",
    ("silver_list_prices_history", "usage_unit"):             "Unit of measure for the usage quantity. DBU for compute, GB for egress, HOUR for connectivity, DAY for clean rooms, DSU for storage.",
    ("silver_list_prices_history", "default_price"):          "Standard list price in USD per usage unit from pricing.default. DECIMAL(18,8) retains source precision and accommodates future sub-cent SKU rates.",
    ("silver_list_prices_history", "pricing_json"):           "Full pricing struct serialised as a JSON string for auditability. Contains default list rate, promotional rate, and effective list rate.",

    # ── silver_usage_history ──────────────────────────────────────────────────
    ("silver_usage_history", "record_identifier"):               "Unique identifier for each Databricks billing usage record. Natural key. 100% unique across 268,127 rows confirmed in EDA. NOT NULL.",
    ("silver_usage_history", "account_identifier"):              "Identifier of the Databricks account associated with this usage record. NOT NULL.",
    ("silver_usage_history", "workspace_identifier"):            "Identifier of the workspace where this usage was incurred. Foreign key to silver_workspace_current. NOT NULL.",
    ("silver_usage_history", "sku_name"):                        "Databricks SKU code identifying the product and compute type. Joins to silver_list_prices_history for cost calculation at gold. NOT NULL.",
    ("silver_usage_history", "cloud"):                           "Cloud provider on which the usage was incurred. AZURE throughout the account.",
    ("silver_usage_history", "usage_date"):                      "Calendar date on which the Databricks usage was recorded. Retained for date-level filtering.",
    ("silver_usage_history", "usage_hour"):                      "Partition key — derived as DATE_TRUNC(HOUR, usage_start_timestamp). One partition per hour of billing activity. NOT NULL.",
    ("silver_usage_history", "usage_start_timestamp"):           "Start timestamp of the usage period. Watermark column. NOT NULL.",
    ("silver_usage_history", "usage_end_timestamp"):             "End timestamp of the usage period for this billing record.",
    ("silver_usage_history", "usage_quantity"):                  "Quantity of compute consumed in this billing event. Unit defined by usage_unit column. Cost derived at gold layer.",
    ("silver_usage_history", "usage_unit"):                      "Unit of measure for the usage quantity. DBU for compute, GB for egress, HOUR for connectivity.",
    ("silver_usage_history", "billing_origin_product"):          "Raw Databricks product category. JOBS, DLT, SQL, ALL_PURPOSE, MODEL_SERVING, APPS etc.",
    ("silver_usage_history", "usage_type"):                      "Billing usage type. COMPUTE_TIME, STORAGE_SPACE, NETWORK_BYTE, NETWORK_HOUR, API_OPERATION, TOKEN, GPU_TIME, ANSWER.",
    ("silver_usage_history", "record_type"):                     "Billing record type. ORIGINAL for standard rows. RETRACTION or RESTATEMENT for correction rows.",
    ("silver_usage_history", "cluster_identifier"):              "Identifier of the cluster that generated this usage record. Foreign key to silver_cluster_current. NULL when not cluster-based.",
    ("silver_usage_history", "warehouse_identifier"):            "Identifier of the SQL warehouse that generated this usage record. Foreign key to silver_warehouse_current. NULL when not warehouse-based.",
    ("silver_usage_history", "job_identifier"):                  "Identifier of the Databricks job that generated this usage record. Foreign key to silver_job_current. NULL when not job-based.",
    ("silver_usage_history", "declarative_pipeline_identifier"): "Identifier of the DLT pipeline that generated this usage record. NULL when not pipeline-based.",
    ("silver_usage_history", "endpoint_identifier"):             "Identifier of the model serving endpoint that generated this usage record. Foreign key to silver_served_entity_current. NULL when not endpoint-based.",
    ("silver_usage_history", "app_name"):                        "Name of the Databricks App that generated this usage record. Sourced from usage_metadata.app_name. NULL when not app-based.",  # ← ADD
    ("silver_usage_history", "job_name"):                        "Display name of the Databricks job associated with this usage record. NULL for non-job billing events.",
    ("silver_usage_history", "executed_by_identity"):            "Email address or system identity of the user or service principal that executed this workload. NULL for serverless SQL warehouse queries by Databricks platform design.",
    ("silver_usage_history", "tag_team_text"):                   "Value of the team tag applied to the billable resource. UNTAGGED sentinel applied at gold for null values.",
    ("silver_usage_history", "tag_domain_text"):                 "Value of the domain tag applied to the billable resource. Normalised at gold. UNTAGGED sentinel applied for null values.",
    ("silver_usage_history", "tag_purpose_text"):                "Value of the purpose tag applied to the billable resource. UNTAGGED sentinel applied at gold for null values.",
    ("silver_usage_history", "custom_tags"):                     "Map of all custom tags applied to the billable resource. MAP<STRING,STRING>. All tag keys accessible via custom_tags[key].",

    # ── silver_cluster_current ────────────────────────────────────────────────
    ("silver_cluster_current", "cluster_identifier"):              "Unique identifier of the Databricks cluster. Primary key. NOT NULL.",
    ("silver_cluster_current", "workspace_identifier"):            "Identifier of the workspace this cluster belongs to. Foreign key to silver_workspace_current. NOT NULL.",
    ("silver_cluster_current", "cluster_name"):                    "Display name of the Databricks cluster as configured.",
    ("silver_cluster_current", "owner_email"):                     "Email address of the user who owns this cluster. Primary owner field for cluster cost attribution. 100% email confirmed from live extract.",
    ("silver_cluster_current", "create_timestamp"):                "Timestamp when this cluster configuration version was created.",
    ("silver_cluster_current", "delete_timestamp"):                "Timestamp when this cluster was deleted. NULL for active clusters.",
    ("silver_cluster_current", "driver_node_type"):                "Code identifying the instance type of the driver node. Confirmed source column name from live extract.",
    ("silver_cluster_current", "worker_node_type"):                "Code identifying the instance type of the worker nodes. Confirmed source column name from live extract.",
    ("silver_cluster_current", "worker_count"):                    "Fixed number of worker nodes configured on this cluster. NULL when autoscaling is configured.",
    ("silver_cluster_current", "autoscale_min_workers"):           "Minimum number of worker nodes this cluster scales down to when autoscaling is enabled.",
    ("silver_cluster_current", "autoscale_max_workers"):           "Maximum number of worker nodes this cluster scales up to when autoscaling is enabled.",
    ("silver_cluster_current", "autotermination_minutes"):         "Number of idle minutes after which this cluster automatically terminates.",
    ("silver_cluster_current", "elastic_disk_enabled_indicator"):  "Flag indicating whether elastic disk autoscaling is enabled on this cluster.",
    ("silver_cluster_current", "custom_tags"):                     "Map of custom tags applied to this cluster. MAP<STRING,STRING>.",
    ("silver_cluster_current", "cluster_source"):                  "Code identifying the mechanism through which this cluster was created. UI, JOB, API, CLONE etc.",
    ("silver_cluster_current", "runtime_version"):                 "Databricks Runtime (DBR) version string configured on this cluster. Confirmed source column name from live extract.",
    ("silver_cluster_current", "change_timestamp"):                "Timestamp of the most recent configuration change. Dedup key — 0 nulls confirmed in live extract. NOT NULL.",
    ("silver_cluster_current", "deleted_indicator"):               "Flag indicating whether this cluster has been deleted. Derived as delete_timestamp IS NOT NULL.",

    # ── silver_warehouse_current ──────────────────────────────────────────────
    ("silver_warehouse_current", "warehouse_identifier"): "Unique identifier of the SQL warehouse. Primary key. NOT NULL.",
    ("silver_warehouse_current", "workspace_identifier"): "Identifier of the workspace this warehouse belongs to. Foreign key to silver_workspace_current. NOT NULL.",
    ("silver_warehouse_current", "warehouse_name"):       "Display name of the SQL warehouse as configured.",
    ("silver_warehouse_current", "warehouse_type"):       "Type of the SQL warehouse. CLASSIC, PRO, or SERVERLESS.",
    ("silver_warehouse_current", "warehouse_channel"):    "Release channel of the SQL warehouse. CURRENT or PREVIEW. Confirmed flat column in live extract.",
    ("silver_warehouse_current", "warehouse_size"):       "Compute size tier of the SQL warehouse. XXSMALL through XXXLARGE.",
    ("silver_warehouse_current", "min_cluster_count"):    "Minimum number of clusters this warehouse scales down to during low demand.",
    ("silver_warehouse_current", "max_cluster_count"):    "Maximum number of clusters this warehouse scales up to during peak demand.",
    ("silver_warehouse_current", "auto_stop_minutes"):    "Number of idle minutes after which this warehouse automatically stops.",
    ("silver_warehouse_current", "creator_identity"):     "Identity of the user or service principal that created this warehouse. May be an email address, numeric system ID, or System-User. Mixed values confirmed from live extract.",
    ("silver_warehouse_current", "custom_tags"):          "Map of custom tags applied to this warehouse. MAP<STRING,STRING>.",
    ("silver_warehouse_current", "change_timestamp"):     "Timestamp of the most recent configuration change. Dedup key — 0 nulls confirmed in live extract. NOT NULL.",
    ("silver_warehouse_current", "delete_timestamp"):     "Timestamp when this warehouse was deleted. NULL for active warehouses.",
    ("silver_warehouse_current", "deleted_indicator"):    "Flag indicating whether this warehouse has been deleted. Derived as delete_timestamp IS NOT NULL.",

    # ── silver_job_current ────────────────────────────────────────────────────
    ("silver_job_current", "job_identifier"):       "Unique identifier of the Databricks job. Primary key. NOT NULL.",
    ("silver_job_current", "workspace_identifier"): "Identifier of the workspace this job belongs to. Foreign key to silver_workspace_current. NOT NULL.",
    ("silver_job_current", "job_name"):             "Display name of the Databricks job as configured.",
    ("silver_job_current", "creator_identifier"):   "System-assigned identifier of the user or service principal that created this job. Holds system IDs not email addresses. Retained for lineage.",
    ("silver_job_current", "creator_identity"):     "Email address of the user who created this job. NULL for 941 of 1,000 rows in live extract. Email when populated — confirmed.",
    ("silver_job_current", "run_as_identifier"):    "System-assigned identifier of the identity under which this job executes. Holds system IDs not email addresses. Retained for lineage.",
    ("silver_job_current", "run_as_identity"):      "Identity under which this job executes. Mixed values — 5.9% email, 6% UUIDs confirmed from live extract.",
    ("silver_job_current", "job_description"):      "Free-text description of this job as entered by the creator. 87 of 1,000 rows populated in live extract.",
    ("silver_job_current", "trigger_type"):         "Type of trigger that executes this job. CRON, PERIODIC etc.",
    ("silver_job_current", "paused_indicator"):     "Flag indicating whether the scheduled trigger for this job is currently paused.",
    ("silver_job_current", "change_timestamp"):     "Timestamp of the most recent configuration change. Dedup key — 0 nulls confirmed in live extract. NOT NULL.",
    ("silver_job_current", "create_timestamp"):     "Timestamp when this job was first created. NULL for most rows in current live extract — retained for future data.",
    ("silver_job_current", "delete_timestamp"):     "Timestamp when this job was deleted. NULL for active jobs.",
    ("silver_job_current", "custom_tags"):          "Map of custom tags applied to this job. MAP<STRING,STRING>.",
    ("silver_job_current", "deleted_indicator"):    "Flag indicating whether this job has been deleted. Derived as delete_timestamp IS NOT NULL.",

    # ── silver_pipeline_current ───────────────────────────────────────────────
    ("silver_pipeline_current", "pipeline_identifier"):  "Unique identifier of the DLT pipeline. Primary key. NOT NULL.",
    ("silver_pipeline_current", "workspace_identifier"): "Identifier of the workspace this pipeline belongs to. Foreign key to silver_workspace_current. NOT NULL.",
    ("silver_pipeline_current", "pipeline_name"):        "Display name of the DLT pipeline as configured.",
    ("silver_pipeline_current", "pipeline_type"):        "Type of the DLT pipeline. MATERIALIZED_VIEW, STREAMING_TABLE, ETL_PIPELINE, INGESTION_PIPELINE, INGESTION_GATEWAY.",
    ("silver_pipeline_current", "creator_email"):        "Email address of the identity that created this pipeline. 99.7% populated in live extract.",
    ("silver_pipeline_current", "run_as_email"):         "Email address of the identity under which this pipeline executes. 99.7% populated in live extract.",
    ("silver_pipeline_current", "custom_tags"):          "Map of custom tags applied to this pipeline. MAP<STRING,STRING>.",
    ("silver_pipeline_current", "settings_json"):        "Full settings configuration of this pipeline serialised as a JSON string from the source struct.",
    ("silver_pipeline_current", "configuration_json"):   "Configuration key-value pairs of this pipeline serialised as a JSON string from the source struct.",
    ("silver_pipeline_current", "change_timestamp"):     "Timestamp of the most recent configuration change. Dedup key — 0 nulls confirmed in live extract. NOT NULL.",
    ("silver_pipeline_current", "create_timestamp"):     "Timestamp when this pipeline was first created.",
    ("silver_pipeline_current", "delete_timestamp"):     "Timestamp when this pipeline was deleted. NULL for active pipelines.",
    ("silver_pipeline_current", "deleted_indicator"):    "Flag indicating whether this pipeline has been deleted. Derived as delete_timestamp IS NOT NULL.",

    # ── silver_served_entity_current ──────────────────────────────────────────
    ("silver_served_entity_current", "served_entity_identifier"):     "Unique identifier of the model serving endpoint entity. Primary key. NOT NULL.",
    ("silver_served_entity_current", "workspace_identifier"):         "Identifier of the workspace this served entity belongs to. Foreign key to silver_workspace_current. NOT NULL.",
    ("silver_served_entity_current", "endpoint_identifier"):          "Identifier of the model serving endpoint containing this entity. NOT NULL.",
    ("silver_served_entity_current", "endpoint_name"):                "Display name of the model serving endpoint.",
    ("silver_served_entity_current", "served_entity_name"):           "Display name of this entity within its serving endpoint.",
    ("silver_served_entity_current", "entity_type"):                  "Type of entity being served. CUSTOM_MODEL for user-deployed models. FOUNDATION_MODEL for Databricks-managed endpoints.",
    ("silver_served_entity_current", "entity_name"):                  "Display name of the model or feature specification being served by this entity.",
    ("silver_served_entity_current", "entity_version"):               "Version identifier of the model or artifact being served. STRING to accommodate future non-numeric versions.",
    ("silver_served_entity_current", "endpoint_config_version"):      "Version number of the endpoint configuration at the time this entity record was captured.",
    ("silver_served_entity_current", "task"):                         "Machine learning task type this served entity is configured to perform. llm/v1/chat or agent/v1/chat.",
    ("silver_served_entity_current", "creator_identity"):             "Identity of the user or service principal that created this served entity. Email for CUSTOM_MODEL, System-User for FOUNDATION_MODEL. Mixed values confirmed from live extract.",
    ("silver_served_entity_current", "custom_model_config_json"):     "Configuration details for custom model entities serialised as a JSON string. Populated for CUSTOM_MODEL entity type.",
    ("silver_served_entity_current", "foundation_model_config_json"): "Configuration details for foundation model entities serialised as a JSON string. Populated for FOUNDATION_MODEL entity type.",
    ("silver_served_entity_current", "change_timestamp"):             "Timestamp of the most recent configuration change. Dedup key — 0 nulls confirmed in live extract. NOT NULL.",
    ("silver_served_entity_current", "delete_timestamp"):             "Timestamp when this served entity was deleted. NULL for active entities.",
    ("silver_served_entity_current", "deleted_indicator"):            "Flag indicating whether this served entity has been deleted. Derived as delete_timestamp IS NOT NULL.",

    # ── gold_dim_workspace ────────────────────────────────────────────────────
    ("gold_dim_workspace", "workspace_sk"):         "Surrogate primary key — xxhash64(CAST(workspace_identifier AS STRING)). Deterministic across daily rebuilds.",
    ("gold_dim_workspace", "workspace_identifier"): "Unique identifier of the source Databricks workspace. Natural key retained for traceability.",
    ("gold_dim_workspace", "workspace_name"):       "Display name of the Databricks workspace as configured.",
    ("gold_dim_workspace", "workspace_url"):        "Full URL of the Databricks workspace.",
    ("gold_dim_workspace", "workspace_status"):     "Current operational status of this workspace. RUNNING, PROVISIONING, FAILED, BANNED, NOT_PROVISIONED.",

    # ── gold_dim_sku ──────────────────────────────────────────────────────────
    ("gold_dim_sku", "sku_sk"):                 "Surrogate primary key — xxhash64(CAST(sku_name AS STRING)). Deterministic across daily rebuilds.",
    ("gold_dim_sku", "sku_name"):               "Databricks SKU code identifying the product and compute type. Natural key retained for traceability.",
    ("gold_dim_sku", "billing_origin_product"): "Raw Databricks product category from source. SQL, ALL_PURPOSE, APPS, JOBS, VECTOR_SEARCH etc.",
    ("gold_dim_sku", "product_family"):         "Derived business grouping for the SKU. Compute, SQL Analytics, Serving, Apps, Clean Rooms, DLT, Model Training, Egress, Storage, Private Connectivity.",
    ("gold_dim_sku", "current_price"):          "Most recent standard list price in USD from silver_list_prices_history. NULL for retired SKUs. DECIMAL(18,8) retains source precision and accommodates future sub-cent SKU rates.",

    # ── gold_dim_object ───────────────────────────────────────────────────────
    ("gold_dim_object", "object_sk"):          "Surrogate primary key — xxhash64(object_identifier || object_type). Deterministic across daily Full Overwrite rebuilds.",
    ("gold_dim_object", "object_identifier"):  "Natural key component — billable object identifier.",
    ("gold_dim_object", "object_type"):        "Natural key component — CLUSTER, WAREHOUSE, JOB, PIPELINE, ENDPOINT.",
    ("gold_dim_object", "object_name"):        "Human-readable label from silver metadata. NULL for deleted objects.",
    ("gold_dim_object", "owner_identity"):     "Resolved identity from COALESCE chain. Email for human owners. Service principal or system identifier for non-human identities. NULL where UNRESOLVED.",
    ("gold_dim_object", "attribution_method"): "How owner was resolved — executed_by_identity, creator_email, creator_identity, owner_email, UNRESOLVED. NOT NULL.",
    ("gold_dim_object", "workspace_sk"):       "Foreign key to gold_dim_workspace.workspace_sk. NOT NULL.",
    ("gold_dim_object", "last_activity_date"): "Most recent usage_date across all billing records for this object. Recalculated on every daily Full Overwrite run.",
    ("gold_dim_object", "idle_day_count"):     "Number of days since last_activity_date. Recalculated on every daily Full Overwrite run.",
    ("gold_dim_object", "deleted_indicator"):  "Flag indicating whether this object has been deleted. Derived from absence in silver metadata tables.",

    # ── gold_fact_usage ───────────────────────────────────────────────────────
    ("gold_fact_usage", "fact_sk"):              "Surrogate primary key — xxhash64 of full grain (usage_hour, workspace_sk, object_sk, sku_sk, tag_team_text, tag_domain_text, tag_purpose_text). COALESCE(-1) applied to nullable SKs and COALESCE(UNTAGGED) to tags before hashing. Deterministic across daily DELETE + INSERT runs.",  # ← ADD
    ("gold_fact_usage", "usage_hour"):           "Hourly partition key — derived as DATE_TRUNC(HOUR, usage_start_timestamp). NOT NULL.",
    ("gold_fact_usage", "usage_date"):           "Calendar date of this usage hour. Retained for date-level filtering without timestamp truncation.",
    ("gold_fact_usage", "workspace_sk"):         "Foreign key to gold_dim_workspace.workspace_sk. NULL for decommissioned workspaces absent from dim table.",
    ("gold_fact_usage", "object_sk"):            "Foreign key to gold_dim_object.object_sk. NULL for UNRESOLVED platform charges with no attributable object.",
    ("gold_fact_usage", "sku_sk"):               "Foreign key to gold_dim_sku.sku_sk. NOT NULL — 100% join coverage confirmed in EDA.",
    ("gold_fact_usage", "tag_team_text"):        "Value of the team tag applied to the billable resource. UNTAGGED sentinel where source tag is null.",
    ("gold_fact_usage", "tag_domain_text"):      "Value of the domain tag applied to the billable resource. UNTAGGED sentinel where source tag is null.",
    ("gold_fact_usage", "tag_purpose_text"):     "Value of the purpose tag applied to the billable resource. UNTAGGED sentinel where source tag is null.",
    ("gold_fact_usage", "total_cost"):           "Sum of usage_cost from silver_usage_history for this grain row. Cost in USD at standard list price.",
    ("gold_fact_usage", "total_usage_quantity"): "Sum of usage_quantity from silver_usage_history for this grain row. Unit varies by SKU — DBU, GB, HOUR, DAY, GPU_HOUR.",
    ("gold_fact_usage", "billing_row_count"):    "Count of silver_usage_history rows aggregated into this grain row.",

    # ── silver_query_history ──────────────────────────────────────────────────
    ("silver_query_history", "query_identifier"):                   "Unique identifier of the query execution. Primary key. NOT NULL. From system.query.history.statement_id.",
    ("silver_query_history", "workspace_identifier"):               "Identifier of the workspace where the query ran. Foreign key to silver_workspace_current. NOT NULL.",
    ("silver_query_history", "executed_by_identity"):               "Email address of the user who ran the query. 100% populated for Claude MCP queries. From executed_by.",
    ("silver_query_history", "warehouse_identifier"):               "Identifier of the SQL warehouse that executed the query. Join key to gold_fact_usage. From compute.warehouse_id.",
    ("silver_query_history", "client_application"):                 "Client tool that submitted the query. Claude values: 'Databricks SQL MCP', 'DatabricksDbsqlMcp'. Dashboard filters on this column directly.",
    ("silver_query_history", "client_driver"):                      "Connector used to connect to Databricks. DatabricksSqlExecApi, 2.0 for all MCP queries. Retained for audit.",
    ("silver_query_history", "execution_status"):                   "Query termination state. Confirmed values: FINISHED, FAILED. All statuses retained at silver. FINISHED only at gold.",
    ("silver_query_history", "statement_type"):                     "SQL statement type. SELECT, DESCRIBE, etc.",
    ("silver_query_history", "result_cache_hit_indicator"):         "TRUE when the query result was served from the Databricks result cache. Near-zero compute consumed when TRUE. From from_result_cache.",
    ("silver_query_history", "start_timestamp"):                    "Timestamp when Databricks received the query request. Watermark column. UTC. NOT NULL. From start_time.",
    ("silver_query_history", "end_timestamp"):                      "Timestamp when the query execution ended. UTC. NOT NULL confirmed for all statuses. From end_time.",
    ("silver_query_history", "query_start_hour"):                   "Partition key — derived as DATE_TRUNC('HOUR', start_timestamp). Hourly grain. Aligns with silver_usage_history.usage_hour. NOT NULL.",
    ("silver_query_history", "query_start_date"):                   "Calendar date of query start — derived as DATE(start_timestamp). Retained for date-level filtering. NOT NULL.",
    ("silver_query_history", "total_duration_ms"):                  "Wall-clock elapsed time from query submission to result delivered in milliseconds. Includes all phases. Reference metric only — do not use for cost attribution.",
    ("silver_query_history", "waiting_for_compute_duration_ms"):    "Time spent waiting for warehouse to provision or warm up in milliseconds. 0.33% null — COALESCE to 0 in dashboard.",
    ("silver_query_history", "waiting_at_capacity_duration_ms"):    "Time spent queued because warehouse was fully occupied in milliseconds. 0.33% null — COALESCE to 0 in dashboard.",
    ("silver_query_history", "compilation_duration_ms"):            "Time spent parsing SQL and generating query plan in milliseconds. 9.64% null for FAILED queries and cache hits — COALESCE to 0.",
    ("silver_query_history", "execution_duration_ms"):              "Wall-clock execution time in milliseconds. 9.69% null for FAILED queries and cache hits. Do NOT use for cost attribution — use total_task_duration_ms instead.",
    ("silver_query_history", "total_task_duration_ms"):             "Sum of CPU time across all parallel tasks in milliseconds. Can exceed wall-clock for parallelized queries. Reflects true DBU consumption. PRIMARY cost attribution metric. 0.37% null — COALESCE to 0.",
    ("silver_query_history", "result_fetch_duration_ms"):           "Time spent transferring result set to client in milliseconds. 0.38% null — COALESCE to 0.",
    ("silver_query_history", "read_rows"):                          "Number of rows read after partition and file pruning. Query complexity indicator.",
    ("silver_query_history", "produced_rows"):                      "Total rows returned by the query. Result set size indicator.",
    ("silver_query_history", "read_bytes"):                         "Bytes read after partition and file pruning. Data scan volume indicator.",
    ("silver_query_history", "session_identifier"):                 "Spark session identifier. Equals query_identifier for Claude MCP queries — one session per query. From session_id.",

    # ── gold_query_history ────────────────────────────────────────────────────
    ("gold_query_history", "query_identifier"):                     "Unique identifier of the query execution. Primary key. NOT NULL. Natural key from silver_query_history.",
    ("gold_query_history", "workspace_identifier"):                 "Identifier of the workspace where the query ran. Foreign key to gold_dim_workspace. NOT NULL.",
    ("gold_query_history", "workspace_name"):                       "Display name of the Databricks workspace. Denormalized from silver_workspace_current. NULL for decommissioned workspaces.",
    ("gold_query_history", "executed_by_identity"):                 "Email address of the executing user. Primary user attribution field for dashboard cost allocation.",
    ("gold_query_history", "warehouse_identifier"):                 "SQL warehouse identifier. Join key to gold_fact_usage for pro-rata cost attribution.",
    ("gold_query_history", "warehouse_name"):                       "Display name of the SQL warehouse. Denormalized from silver_warehouse_current. NULL for deleted warehouses.",
    ("gold_query_history", "client_application"):                   "Client tool that submitted the query. Claude filter: IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp'). Dashboard filters on this column directly.",
    ("gold_query_history", "client_driver"):                        "Connector used. Retained for audit.",
    ("gold_query_history", "execution_status"):                     "Always FINISHED at gold. FAILED and CANCELED excluded — profiling confirmed FAILED = 0.01% of total task seconds.",
    ("gold_query_history", "statement_type"):                       "SQL statement type. SELECT, DESCRIBE, etc.",
    ("gold_query_history", "result_cache_hit_indicator"):           "TRUE when result served from cache — near-zero compute. Retained for attribution accuracy audit and cache hit rate dashboard metric.",
    ("gold_query_history", "start_timestamp"):                      "Query start timestamp. UTC. NOT NULL.",
    ("gold_query_history", "end_timestamp"):                        "Query end timestamp. UTC. NOT NULL confirmed for all statuses.",
    ("gold_query_history", "query_start_hour"):                     "Partition key — hourly grain. Aligns with gold_fact_usage.usage_hour for future hour-level joins. NOT NULL.",
    ("gold_query_history", "query_start_date"):                     "Calendar date — retained for date-level filtering and joins to gold_fact_usage. NOT NULL.",
    ("gold_query_history", "total_duration_ms"):                    "Wall-clock total duration. Reference metric only.",
    ("gold_query_history", "waiting_for_compute_duration_ms"):      "Cold start wait time in milliseconds. Warehouse health indicator. COALESCE to 0 in dashboard.",
    ("gold_query_history", "waiting_at_capacity_duration_ms"):      "Queue wait time in milliseconds. Warehouse capacity contention indicator. COALESCE to 0 in dashboard.",
    ("gold_query_history", "compilation_duration_ms"):              "Query planning time in milliseconds. 9.64% null. COALESCE to 0 in dashboard.",
    ("gold_query_history", "execution_duration_ms"):                "Execution wall-clock in milliseconds. 9.69% null. Do NOT use for cost attribution.",
    ("gold_query_history", "total_task_duration_ms"):               "PRIMARY cost attribution metric. Sum of all parallel task CPU time in milliseconds. 0.37% null — COALESCE to 0.",
    ("gold_query_history", "result_fetch_duration_ms"):             "Result transfer time in milliseconds. COALESCE to 0 in dashboard.",
    ("gold_query_history", "read_rows"):                            "Rows scanned after pruning. Query complexity indicator.",
    ("gold_query_history", "produced_rows"):                        "Result set row count.",
    ("gold_query_history", "read_bytes"):                           "Data scan volume in bytes.",
    ("gold_query_history", "session_identifier"):                   "Session identifier. Retained for audit.",
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 6 - create_table helper
# MAGIC Per Science PySpark + Notebook Coding Conventions.
# MAGIC Builds DDL from a DataFrame schema, injects column comments, and writes
# MAGIC the empty DataFrame to materialise the table in Unity Catalog.
# MAGIC Supports optional partition_cols for partitioned tables.

# COMMAND ----------

def create_table(
    df: DataFrame,
    catalog_name: str,
    schema_name: str,
    table_name: str,
    description: str,
    column_comments: dict = None,
    owner: str = None,
    partition_cols: list = None,
):
    full_table_name = f"{catalog_name}.{schema_name}.{table_name}"

    # ── Filter DD to this table's entries only ────────────────────────────────
    # DD is keyed by (table_name, column_name) tuples.
    # Extract only the entries matching this table before looking up comments.
    table_dd = {
        k[1]: v
        for k, v in (column_comments or {}).items()
        if isinstance(k, tuple) and k[0] == table_name
    }

    # ── Build column definitions ──────────────────────────────────────────────
    cols = []
    for field in df.schema.fields:
        col_name = field.name
        col_type = field.dataType.simpleString().upper()
        col_comment = ""
        if table_dd and col_name in table_dd:
            escaped = table_dd[col_name].replace("'", "''")
            col_comment = f" COMMENT '{escaped}'"
        cols.append(f"`{col_name}` {col_type}{col_comment}")

    col_defs = ",\n      ".join(cols)

    partition_clause = ""
    if partition_cols:
        partition_clause = f"\n    PARTITIONED BY ({', '.join(partition_cols)})"

    ddl = "CREATE TABLE IF NOT EXISTS {} (\n      {}\n    ) USING delta{} COMMENT '{}'".format(
        full_table_name,
        col_defs,
        partition_clause,
        description.replace("'", "''")
    )

    spark.sql(ddl)
    df.write.mode("overwrite").insertInto(full_table_name, overwrite=True)

    if owner:
        spark.sql(f"ALTER TABLE {full_table_name} OWNER TO `{owner}`")

    if verbose:
        print(f"  created: {full_table_name}")


def set_primary_key(
    catalog: str,
    schema: str,
    table: str,
    pk_col: str,
    not_null_cols: list[str] = None,
) -> None:
    """
    Enforces NOT NULL and declares PK on a Delta table after create_table.
    Databricks requires NOT NULL at Delta level before PK constraint can be added.
    """
    full_name = f"{catalog}.{schema}.{table}"
    cols_to_enforce = not_null_cols or [pk_col]
    for col in cols_to_enforce:
        spark.sql(f"ALTER TABLE {full_name} ALTER COLUMN {col} SET NOT NULL")
    spark.sql(
        f"ALTER TABLE {full_name} "
        f"ADD CONSTRAINT {table}_pk PRIMARY KEY ({pk_col})"
    )
    if verbose:
        print(f"  pk set : {full_name} ({pk_col})")


def set_foreign_key(
    catalog: str,
    schema: str,
    table: str,
    fk_name: str,
    fk_cols: list[str],
    ref_table: str,
    ref_cols: list[str],
) -> None:
    full_table = f"{catalog}.{schema}.{table}"
    full_ref   = f"{catalog}.{schema}.{ref_table}"
    cols         = ", ".join(fk_cols)
    ref_cols_str = ", ".join(ref_cols)
    spark.sql(f"""
        ALTER TABLE {full_table}
        ADD CONSTRAINT {fk_name}
        FOREIGN KEY ({cols})
        REFERENCES {full_ref} ({ref_cols_str})
    """)
    if verbose:
        print(f"  fk set : {full_table} ({cols}) → {full_ref} ({ref_cols_str})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 7 - Schema creation and table drop
# MAGIC Creates the schema if it does not exist.
# MAGIC Drops all tables so schema changes take effect on rerun.
# MAGIC Guarded by `initial_full_load` — already asserted True by Cell 4.

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {target_catalog}.{SCHEMA}")
spark.sql(f"ALTER SCHEMA {target_catalog}.{SCHEMA} OWNER TO `{OWNER}`")

for tbl in [
    "silver_workspace_current",
    "silver_list_prices_history",
    "silver_usage_history",
    "silver_cluster_current",
    "silver_warehouse_current",
    "silver_job_current",
    "silver_pipeline_current",
    "silver_served_entity_current",
    "silver_query_history",
    "gold_dim_workspace",
    "gold_dim_sku",
    "gold_dim_object",
    "gold_fact_usage",
    "gold_query_history",
]:
    fqn = f"{target_catalog}.{SCHEMA}.{tbl}"
    spark.sql(f"DROP TABLE IF EXISTS {fqn}")
    if verbose:
        print(f"  dropped: {fqn}")

# end of the code

# COMMAND ----------

# MAGIC %md
# MAGIC ### silver_workspace_current
# MAGIC Full Overwite

# COMMAND ----------

silver_workspace_current_struct = T.StructType([
    T.StructField("workspace_identifier",         T.StringType(),    False),
    T.StructField("account_identifier",           T.StringType(),    False),
    T.StructField("workspace_name",               T.StringType(),    True),
    T.StructField("workspace_url",                T.StringType(),    True),
    T.StructField("workspace_creation_timestamp", T.TimestampType(), True),
    T.StructField("workspace_status",             T.StringType(),    True),
])

create_table(
    df=spark.createDataFrame([], silver_workspace_current_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="silver_workspace_current",
    description="Current state of every Databricks workspace. One row per workspace. Full Overwrite. Source: system.access.workspaces_latest.",
    column_comments=DD,
    owner=OWNER,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### silver_list_prices_history
# MAGIC Full Overwrite. Price reference table. Standalone — no FK.
# MAGIC Source: system.billing.list_prices

# COMMAND ----------

silver_list_prices_history_struct = T.StructType([
    T.StructField("sku_name",               T.StringType(),                   False),
    T.StructField("price_start_timestamp",  T.TimestampType(),                False),
    T.StructField("price_end_timestamp",    T.TimestampType(),                True),
    T.StructField("cloud",                  T.StringType(),                   True),
    T.StructField("currency_code",          T.StringType(),                   True),
    T.StructField("usage_unit",             T.StringType(),                   True),
    T.StructField("default_price",          T.DecimalType(18, 8),             True),
    T.StructField("pricing_json",           T.StringType(),                   True),
])

create_table(
    df=spark.createDataFrame([], silver_list_prices_history_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="silver_list_prices_history",
    description="Complete price history for every Databricks SKU. One row per SKU per price effective period. Full Overwrite every run. Source: system.billing.list_prices.",
    column_comments=DD,
    owner=OWNER,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### silver_usage_history
# MAGIC Append with Watermark. Partitioned by usage_hour.
# MAGIC Central fact table at silver. Source: system.billing.usage

# COMMAND ----------

# DBTITLE 1,silver_usage_history
silver_usage_history_struct = T.StructType([
    T.StructField("record_identifier",               T.StringType(),                            False),
    T.StructField("account_identifier",              T.StringType(),                            False),
    T.StructField("workspace_identifier",            T.StringType(),                            False),
    T.StructField("sku_name",                        T.StringType(),                            False),
    T.StructField("cloud",                           T.StringType(),                            True),
    T.StructField("usage_date",                      T.DateType(),                              False),
    T.StructField("usage_hour",                      T.TimestampType(),                         False),
    T.StructField("usage_start_timestamp",           T.TimestampType(),                         False),
    T.StructField("usage_end_timestamp",             T.TimestampType(),                         True),
    T.StructField("usage_quantity",                  T.DecimalType(18, 6),                      True),
    T.StructField("usage_unit",                      T.StringType(),                            True),
    T.StructField("billing_origin_product",          T.StringType(),                            True),
    T.StructField("usage_type",                      T.StringType(),                            True),
    T.StructField("record_type",                     T.StringType(),                            True),
    T.StructField("cluster_identifier",              T.StringType(),                            True),
    T.StructField("warehouse_identifier",            T.StringType(),                            True),
    T.StructField("job_identifier",                  T.StringType(),                            True),
    T.StructField("declarative_pipeline_identifier", T.StringType(),                            True),
    T.StructField("endpoint_identifier",             T.StringType(),                            True),
    T.StructField("app_name",                        T.StringType(),                            True),  # ← ADD
    T.StructField("job_name",                        T.StringType(),                            True),
    T.StructField("executed_by_identity",            T.StringType(),                            True),
    T.StructField("tag_team_text",                   T.StringType(),                            True),
    T.StructField("tag_domain_text",                 T.StringType(),                            True),
    T.StructField("tag_purpose_text",                T.StringType(),                            True),
    T.StructField("custom_tags",                     T.MapType(T.StringType(), T.StringType()), True),
])

create_table(
    df=spark.createDataFrame([], silver_usage_history_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="silver_usage_history",
    description="Databricks billing usage events. One row per billing record. Partitioned by usage_hour. Watermark on usage_start_timestamp. Source: system.billing.usage.",
    column_comments=DD,
    owner=OWNER,
    partition_cols=["usage_hour"],
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### silver_cluster_current
# MAGIC Full Overwrite with ROW_NUMBER() Deduplication.
# MAGIC Source: system.compute.clusters

# COMMAND ----------

silver_cluster_current_struct = T.StructType([
    T.StructField("cluster_identifier",              T.StringType(),                            False),
    T.StructField("workspace_identifier",            T.StringType(),                            False),
    T.StructField("cluster_name",                    T.StringType(),                            True),
    T.StructField("owner_email",                     T.StringType(),                            True),
    T.StructField("create_timestamp",                T.TimestampType(),                         True),
    T.StructField("delete_timestamp",                T.TimestampType(),                         True),
    T.StructField("driver_node_type",                T.StringType(),                            True),
    T.StructField("worker_node_type",                T.StringType(),                            True),
    T.StructField("worker_count",                    T.IntegerType(),                           True),
    T.StructField("autoscale_min_workers",           T.IntegerType(),                           True),
    T.StructField("autoscale_max_workers",           T.IntegerType(),                           True),
    T.StructField("autotermination_minutes",         T.IntegerType(),                           True),
    T.StructField("elastic_disk_enabled_indicator",  T.BooleanType(),                           True),
    T.StructField("custom_tags",                     T.MapType(T.StringType(), T.StringType()), True),
    T.StructField("cluster_source",                  T.StringType(),                            True),
    T.StructField("runtime_version",                 T.StringType(),                            True),
    T.StructField("change_timestamp",                T.TimestampType(),                         False),
    T.StructField("deleted_indicator",               T.BooleanType(),                           True),
])

create_table(
    df=spark.createDataFrame([], silver_cluster_current_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="silver_cluster_current",
    description="Current configuration of every Databricks cluster. One row per cluster after dedup. Dedup key: change_timestamp DESC. Source: system.compute.clusters.",
    column_comments=DD,
    owner=OWNER,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### silver_warehouse_current
# MAGIC Full Overwrite with ROW_NUMBER() Deduplication.
# MAGIC Source: system.compute.warehouses

# COMMAND ----------

silver_warehouse_current_struct = T.StructType([
    T.StructField("warehouse_identifier", T.StringType(),                            False),
    T.StructField("workspace_identifier", T.StringType(),                            False),
    T.StructField("warehouse_name",       T.StringType(),                            True),
    T.StructField("warehouse_type",       T.StringType(),                            True),
    T.StructField("warehouse_channel",    T.StringType(),                            True),
    T.StructField("warehouse_size",       T.StringType(),                            True),
    T.StructField("min_cluster_count",    T.IntegerType(),                           True),
    T.StructField("max_cluster_count",    T.IntegerType(),                           True),
    T.StructField("auto_stop_minutes",    T.IntegerType(),                           True),
    T.StructField("creator_identity",     T.StringType(),                            True),
    T.StructField("custom_tags",          T.MapType(T.StringType(), T.StringType()), True),
    T.StructField("change_timestamp",     T.TimestampType(),                         False),
    T.StructField("delete_timestamp",     T.TimestampType(),                         True),
    T.StructField("deleted_indicator",    T.BooleanType(),                           True),
])

create_table(
    df=spark.createDataFrame([], silver_warehouse_current_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="silver_warehouse_current",
    description="Current configuration of every Databricks SQL warehouse. One row per warehouse after dedup. Dedup key: change_timestamp DESC. Source: system.compute.warehouses.",
    column_comments=DD,
    owner=OWNER,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### silver_job_current
# MAGIC Full Overwrite with ROW_NUMBER() Deduplication.
# MAGIC Source: system.lakeflow.jobs

# COMMAND ----------

silver_job_current_struct = T.StructType([
    T.StructField("job_identifier",       T.StringType(),                            False),
    T.StructField("workspace_identifier", T.StringType(),                            False),
    T.StructField("job_name",             T.StringType(),                            True),
    T.StructField("creator_identifier",   T.StringType(),                            True),
    T.StructField("creator_identity",     T.StringType(),                            True),  # ← UPDATED
    T.StructField("run_as_identifier",    T.StringType(),                            True),
    T.StructField("run_as_identity",      T.StringType(),                            True),
    T.StructField("job_description",      T.StringType(),                            True),
    T.StructField("trigger_type",         T.StringType(),                            True),
    T.StructField("paused_indicator",     T.BooleanType(),                           True),
    T.StructField("change_timestamp",     T.TimestampType(),                         False),
    T.StructField("create_timestamp",     T.TimestampType(),                         True),
    T.StructField("delete_timestamp",     T.TimestampType(),                         True),
    T.StructField("custom_tags",          T.MapType(T.StringType(), T.StringType()), True),
    T.StructField("deleted_indicator",    T.BooleanType(),                           True),
])

create_table(
    df=spark.createDataFrame([], silver_job_current_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="silver_job_current",
    description="Current configuration of every Databricks job. One row per job after dedup. Dedup key: change_timestamp DESC. No reliable email owner field — creator_identity NULL for 94% of rows. Source: system.lakeflow.jobs.",  # ← UPDATED
    column_comments=DD,
    owner=OWNER,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### silver_pipeline_current
# MAGIC Full Overwrite with ROW_NUMBER() Deduplication.
# MAGIC Source: system.lakeflow.pipelines

# COMMAND ----------

silver_pipeline_current_struct = T.StructType([
    T.StructField("pipeline_identifier",  T.StringType(),                            False),
    T.StructField("workspace_identifier", T.StringType(),                            False),
    T.StructField("pipeline_name",        T.StringType(),                            True),
    T.StructField("pipeline_type",        T.StringType(),                            True),
    T.StructField("creator_email",        T.StringType(),                            True),
    T.StructField("run_as_email",         T.StringType(),                            True),
    T.StructField("custom_tags",          T.MapType(T.StringType(), T.StringType()), True),
    T.StructField("settings_json",        T.StringType(),                            True),
    T.StructField("configuration_json",   T.StringType(),                            True),
    T.StructField("change_timestamp",     T.TimestampType(),                         False),
    T.StructField("create_timestamp",     T.TimestampType(),                         True),
    T.StructField("delete_timestamp",     T.TimestampType(),                         True),
    T.StructField("deleted_indicator",    T.BooleanType(),                           True),
])

create_table(
    df=spark.createDataFrame([], silver_pipeline_current_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="silver_pipeline_current",
    description="Current configuration of every DLT pipeline. One row per pipeline after dedup. Dedup key: change_timestamp DESC. creator_email 100% populated — most reliable owner field. Source: system.lakeflow.pipelines.",
    column_comments=DD,
    owner=OWNER,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### silver_served_entity_current
# MAGIC Full Overwrite with ROW_NUMBER() Deduplication.
# MAGIC Source: system.serving.served_entities

# COMMAND ----------

silver_served_entity_current_struct = T.StructType([
    T.StructField("served_entity_identifier",     T.StringType(),  False),
    T.StructField("workspace_identifier",         T.StringType(),  False),
    T.StructField("endpoint_identifier",          T.StringType(),  True),
    T.StructField("endpoint_name",                T.StringType(),  True),
    T.StructField("served_entity_name",           T.StringType(),  True),
    T.StructField("entity_type",                  T.StringType(),  True),
    T.StructField("entity_name",                  T.StringType(),  True),
    T.StructField("entity_version",               T.StringType(),  True),
    T.StructField("endpoint_config_version",      T.IntegerType(), True),
    T.StructField("task",                         T.StringType(),  True),
    T.StructField("creator_identity",             T.StringType(),  True),
    T.StructField("custom_model_config_json",     T.StringType(),  True),
    T.StructField("foundation_model_config_json", T.StringType(),  True),
    T.StructField("change_timestamp",             T.TimestampType(), False),
    T.StructField("delete_timestamp",             T.TimestampType(), True),
    T.StructField("deleted_indicator",            T.BooleanType(),   True),
])

create_table(
    df=spark.createDataFrame([], silver_served_entity_current_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="silver_served_entity_current",
    description="Current configuration of every model serving endpoint entity. One row per entity after dedup. Dedup key: change_timestamp DESC. FOUNDATION_MODEL rows have creator_identity = System-User — UNRESOLVED at gold. Source: system.serving.served_entities.",
    column_comments=DD,
    owner=OWNER,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### silver_query_history
# MAGIC Append with Watermark. Partitioned by query_start_hour.
# MAGIC Query execution history — all execution statuses retained at silver.
# MAGIC Source: system.query.history

# COMMAND ----------

silver_query_history_struct = T.StructType([
    T.StructField("query_identifier",                 T.StringType(),    False),
    T.StructField("workspace_identifier",             T.StringType(),    False),
    T.StructField("executed_by_identity",             T.StringType(),    True),
    T.StructField("warehouse_identifier",             T.StringType(),    True),
    T.StructField("client_application",               T.StringType(),    True),
    T.StructField("client_driver",                    T.StringType(),    True),
    T.StructField("execution_status",                 T.StringType(),    True),
    T.StructField("statement_type",                   T.StringType(),    True),
    T.StructField("result_cache_hit_indicator",       T.BooleanType(),   True),
    T.StructField("start_timestamp",                  T.TimestampType(), False),
    T.StructField("end_timestamp",                    T.TimestampType(), True),
    T.StructField("query_start_hour",                 T.TimestampType(), False),
    T.StructField("query_start_date",                 T.DateType(),      False),
    T.StructField("total_duration_ms",                T.LongType(),      True),
    T.StructField("waiting_for_compute_duration_ms",  T.LongType(),      True),
    T.StructField("waiting_at_capacity_duration_ms",  T.LongType(),      True),
    T.StructField("compilation_duration_ms",          T.LongType(),      True),
    T.StructField("execution_duration_ms",            T.LongType(),      True),
    T.StructField("total_task_duration_ms",           T.LongType(),      True),
    T.StructField("result_fetch_duration_ms",         T.LongType(),      True),
    T.StructField("read_rows",                        T.LongType(),      True),
    T.StructField("produced_rows",                    T.LongType(),      True),
    T.StructField("read_bytes",                       T.LongType(),      True),
    T.StructField("session_identifier",               T.StringType(),    True),
])

create_table(
    df=spark.createDataFrame([], silver_query_history_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="silver_query_history",
    description="Query execution history. One row per query execution — all statuses retained. Partitioned by query_start_hour. Watermark on start_timestamp. Source: system.query.history.",
    column_comments=DD,
    owner=OWNER,
    partition_cols=["query_start_hour"],
)

set_primary_key(
    catalog=target_catalog,
    schema=SCHEMA,
    table="silver_query_history",
    pk_col="query_identifier",
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### gold_dim_workspace
# MAGIC Full Overwrite. Workspace label lookup dimension.
# MAGIC Source: silver_workspace_current

# COMMAND ----------

gold_dim_workspace_struct = T.StructType([
    T.StructField("workspace_sk",         T.LongType(),   False),
    T.StructField("workspace_identifier", T.StringType(), False),
    T.StructField("workspace_name",       T.StringType(), True),
    T.StructField("workspace_url",        T.StringType(), True),
    T.StructField("workspace_status",     T.StringType(), True),
])

create_table(
    df=spark.createDataFrame([], gold_dim_workspace_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="gold_dim_workspace",
    description="Workspace dimension. One row per workspace. Surrogate key derived as xxhash64(workspace_identifier). Source: silver_workspace_current.",
    column_comments=DD,
    owner=OWNER,
)

set_primary_key(
    catalog = target_catalog,
    schema  = SCHEMA,
    table   = "gold_dim_workspace",
    pk_col  = "workspace_sk",
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### gold_dim_sku
# MAGIC Full Overwrite. SKU and product family dimension.
# MAGIC Source: silver_list_prices_history

# COMMAND ----------

gold_dim_sku_struct = T.StructType([
    T.StructField("sku_sk",                 T.LongType(),         False),
    T.StructField("sku_name",               T.StringType(),       False),
    T.StructField("billing_origin_product", T.StringType(),       True),
    T.StructField("product_family",         T.StringType(),       True),
    T.StructField("current_price",          T.DecimalType(18, 8), True),
])

create_table(
    df=spark.createDataFrame([], gold_dim_sku_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="gold_dim_sku",
    description="SKU dimension. One row per SKU. Surrogate key derived as xxhash64(sku_name). Product family is a derived business grouping. Source: silver_list_prices_history.",
    column_comments=DD,
    owner=OWNER,
)

set_primary_key(
    catalog = target_catalog,
    schema  = SCHEMA,
    table   = "gold_dim_sku",
    pk_col  = "sku_sk",
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### gold_dim_object
# MAGIC Full Overwrite. Billable object dimension with owner resolution.
# MAGIC Source: silver_usage_history + all five silver _current metadata tables

# COMMAND ----------

gold_dim_object_struct = T.StructType([
    T.StructField("object_sk",          T.LongType(),    False),
    T.StructField("object_identifier",  T.StringType(),  False),
    T.StructField("object_type",        T.StringType(),  False),
    T.StructField("object_name",        T.StringType(),  True),
    T.StructField("owner_identity",     T.StringType(),  True),
    T.StructField("attribution_method", T.StringType(),  False),
    T.StructField("workspace_sk",       T.LongType(),    False),
    T.StructField("last_activity_date", T.DateType(),    True),
    T.StructField("idle_day_count",     T.IntegerType(), True),
    T.StructField("deleted_indicator",  T.BooleanType(), True),
])

create_table(
    df=spark.createDataFrame([], gold_dim_object_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="gold_dim_object",
    description="Billable object dimension. One row per billable object (current state). Surrogate key derived as xxhash64(object_identifier || object_type). Owner resolved via COALESCE chain. Source: silver_usage_history + silver metadata tables.",
    column_comments=DD,
    owner=OWNER,
)

set_primary_key(
    catalog       = target_catalog,
    schema        = SCHEMA,
    table         = "gold_dim_object",
    pk_col        = "object_sk",
    not_null_cols = ["object_sk", "workspace_sk"],  # workspace_sk is FK — also NOT NULL
)

set_foreign_key(
    catalog   = target_catalog,
    schema    = SCHEMA,
    table     = "gold_dim_object",
    fk_name   = "fk_gold_dim_object_workspace_sk",
    fk_cols   = ["workspace_sk"],
    ref_table = "gold_dim_workspace",
    ref_cols  = ["workspace_sk"],
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### gold_fact_usage
# MAGIC delete+Insert
# MAGIC Central hourly spend fact table.
# MAGIC Source: silver_usage_history

# COMMAND ----------

gold_fact_usage_struct = T.StructType([
    # ── Surrogate key ─────────────────────────────────────────────────────────
    T.StructField("fact_sk",              T.LongType(),         False),  # ← ADD
    # ── Partition key ─────────────────────────────────────────────────────────
    T.StructField("usage_hour",           T.TimestampType(),    False),
    T.StructField("usage_date",           T.DateType(),         False),
    # ── FK to dims ────────────────────────────────────────────────────────────
    T.StructField("workspace_sk",         T.LongType(),         True),
    T.StructField("object_sk",            T.LongType(),         True),
    T.StructField("sku_sk",               T.LongType(),         False),
    # ── Tags ──────────────────────────────────────────────────────────────────
    T.StructField("tag_team_text",        T.StringType(),       True),
    T.StructField("tag_domain_text",      T.StringType(),       True),
    T.StructField("tag_purpose_text",     T.StringType(),       True),
    # ── Measures ──────────────────────────────────────────────────────────────
    T.StructField("total_cost",           T.DecimalType(18, 2), True),
    T.StructField("total_usage_quantity", T.DecimalType(18, 6), True),
    T.StructField("billing_row_count",    T.LongType(),         True),
])

create_table(
    df=spark.createDataFrame([], gold_fact_usage_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="gold_fact_usage",
    description="Hourly spend fact table. One row per workspace x object x SKU x usage_hour. fact_sk is a surrogate PK — xxhash64 of full grain. DELETE + INSERT — partition-selective, historical partitions untouched. Source: silver_usage_history.",
    column_comments=DD,
    owner=OWNER,
    partition_cols=["usage_hour"],
)

set_primary_key(
    catalog       = target_catalog,
    schema        = SCHEMA,
    table         = "gold_fact_usage",
    pk_col        = "fact_sk",                         # ← simplified to single column
    not_null_cols = ["fact_sk","usage_hour", "sku_sk"],              # ← tags removed, fact_sk added
)

set_foreign_key(
    catalog   = target_catalog,
    schema    = SCHEMA,
    table     = "gold_fact_usage",
    fk_name   = "fk_gold_fact_usage_workspace_sk",
    fk_cols   = ["workspace_sk"],
    ref_table = "gold_dim_workspace",
    ref_cols  = ["workspace_sk"],
)

set_foreign_key(
    catalog   = target_catalog,
    schema    = SCHEMA,
    table     = "gold_fact_usage",
    fk_name   = "fk_gold_fact_usage_object_sk",
    fk_cols   = ["object_sk"],
    ref_table = "gold_dim_object",
    ref_cols  = ["object_sk"],
)

set_foreign_key(
    catalog   = target_catalog,
    schema    = SCHEMA,
    table     = "gold_fact_usage",
    fk_name   = "fk_gold_fact_usage_sku_sk",
    fk_cols   = ["sku_sk"],
    ref_table = "gold_dim_sku",
    ref_cols  = ["sku_sk"],
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### gold_query_history
# MAGIC DELETE + INSERT. Partitioned by query_start_hour.
# MAGIC FINISHED queries only — FAILED excluded (0.01% of task seconds, confirmed by profiling).
# MAGIC Denormalized with warehouse_name and workspace_name.
# MAGIC Source: silver_query_history + silver_warehouse_current + silver_workspace_current

# COMMAND ----------

gold_query_history_struct = T.StructType([
    T.StructField("query_identifier",                 T.StringType(),    False),
    T.StructField("workspace_identifier",             T.StringType(),    False),
    T.StructField("workspace_name",                   T.StringType(),    True),
    T.StructField("executed_by_identity",             T.StringType(),    True),
    T.StructField("warehouse_identifier",             T.StringType(),    True),
    T.StructField("warehouse_name",                   T.StringType(),    True),
    T.StructField("client_application",               T.StringType(),    True),
    T.StructField("client_driver",                    T.StringType(),    True),
    T.StructField("execution_status",                 T.StringType(),    False),
    T.StructField("statement_type",                   T.StringType(),    True),
    T.StructField("result_cache_hit_indicator",       T.BooleanType(),   True),
    T.StructField("start_timestamp",                  T.TimestampType(), False),
    T.StructField("end_timestamp",                    T.TimestampType(), True),
    T.StructField("query_start_hour",                 T.TimestampType(), False),
    T.StructField("query_start_date",                 T.DateType(),      False),
    T.StructField("total_duration_ms",                T.LongType(),      True),
    T.StructField("waiting_for_compute_duration_ms",  T.LongType(),      True),
    T.StructField("waiting_at_capacity_duration_ms",  T.LongType(),      True),
    T.StructField("compilation_duration_ms",          T.LongType(),      True),
    T.StructField("execution_duration_ms",            T.LongType(),      True),
    T.StructField("total_task_duration_ms",           T.LongType(),      True),
    T.StructField("result_fetch_duration_ms",         T.LongType(),      True),
    T.StructField("read_rows",                        T.LongType(),      True),
    T.StructField("produced_rows",                    T.LongType(),      True),
    T.StructField("read_bytes",                       T.LongType(),      True),
    T.StructField("session_identifier",               T.StringType(),    True),
])

create_table(
    df=spark.createDataFrame([], gold_query_history_struct),
    catalog_name=target_catalog,
    schema_name=SCHEMA,
    table_name="gold_query_history",
    description="Gold query execution history. One row per FINISHED query execution. FAILED excluded — profiling confirmed 0.01% of total task seconds. Partitioned by query_start_hour. DELETE + INSERT partition-selective. Denormalized with warehouse_name and workspace_name. Source: silver_query_history + silver_warehouse_current + silver_workspace_current.",
    column_comments=DD,
    owner=OWNER,
    partition_cols=["query_start_hour"],
)

set_primary_key(
    catalog=target_catalog,
    schema=SCHEMA,
    table="gold_query_history",
    pk_col="query_identifier",
)

# COMMAND ----------

# DBTITLE 1,gold_top_cost_objects_current - View
def sql_comment(table, col):
    """Look up a column comment from the tuple-keyed DD dict."""
    return DD.get((table, col), "").replace("'", "''")

spark.sql(f"""
    CREATE OR REPLACE VIEW {target_catalog}.{SCHEMA}.gold_top_cost_objects_current (
        object_identifier  COMMENT '{sql_comment("gold_dim_object",    "object_identifier")}',
        object_type        COMMENT '{sql_comment("gold_dim_object",    "object_type")}',
        object_name        COMMENT '{sql_comment("gold_dim_object",    "object_name")}',
        owner_identity     COMMENT '{sql_comment("gold_dim_object",    "owner_identity")}',
        attribution_method COMMENT '{sql_comment("gold_dim_object",    "attribution_method")}',
        workspace_sk       COMMENT '{sql_comment("gold_dim_object",    "workspace_sk")}',
        workspace_name     COMMENT '{sql_comment("gold_dim_workspace", "workspace_name")}',
        last_activity_date COMMENT '{sql_comment("gold_dim_object",    "last_activity_date")}',
        idle_day_count     COMMENT '{sql_comment("gold_dim_object",    "idle_day_count")}',
        deleted_indicator  COMMENT '{sql_comment("gold_dim_object",    "deleted_indicator")}',
        total_cost         COMMENT '{sql_comment("gold_fact_usage",    "total_cost")}',
        cost_rank          COMMENT 'RANK() of this object by total_cost descending. Rank 1 = highest spend.'
    )
    COMMENT 'Top cost objects view. One row per billable object with lifetime spend and cost rank. Answers BQ3 and BQ4. Source: gold_fact_usage JOIN gold_dim_object JOIN gold_dim_workspace.'
    AS
    SELECT
        o.object_identifier,
        o.object_type,
        o.object_name,
        o.owner_identity,
        o.attribution_method,
        o.workspace_sk,
        w.workspace_name,
        o.last_activity_date,
        o.idle_day_count,
        o.deleted_indicator,
        SUM(f.total_cost)                             AS total_cost,
        RANK() OVER (ORDER BY SUM(f.total_cost) DESC) AS cost_rank
    FROM {target_catalog}.{SCHEMA}.gold_fact_usage         f
    JOIN {target_catalog}.{SCHEMA}.gold_dim_object         o
        ON f.object_sk = o.object_sk
    LEFT JOIN {target_catalog}.{SCHEMA}.gold_dim_workspace w
        ON o.workspace_sk = w.workspace_sk
    GROUP BY
        o.object_identifier,
        o.object_type,
        o.object_name,
        o.owner_identity,
        o.attribution_method,
        o.workspace_sk,
        w.workspace_name,
        o.last_activity_date,
        o.idle_day_count,
        o.deleted_indicator
""")

# COMMAND ----------

# DBTITLE 1,gold_daily_spend_trend
spark.sql(f"""
    CREATE OR REPLACE VIEW {target_catalog}.{SCHEMA}.gold_daily_spend_trend (
        usage_date              COMMENT '{sql_comment("gold_fact_usage", "usage_date")}',
        total_usage_quantity    COMMENT '{sql_comment("gold_fact_usage", "total_usage_quantity")}',
        daily_cost              COMMENT 'Total cost in USD for this calendar date. SUM(total_cost) from gold_fact_usage grouped by usage_date.',
        rolling_30_day_avg_cost COMMENT '30-day rolling average daily cost. Window: 29 PRECEDING rows to CURRENT ROW ordered by usage_date.',
        rolling_7_day_avg_cost  COMMENT '7-day rolling average daily cost. Window: 6 PRECEDING rows to CURRENT ROW ordered by usage_date.'
    )
    COMMENT 'Daily spend trend view. One row per calendar date. Aggregates hourly gold_fact_usage to daily totals with 7-day and 30-day rolling averages. Answers BQ2. Source: gold_fact_usage.'
    AS
    SELECT
        f.usage_date,
        SUM(f.total_usage_quantity)                                    AS total_usage_quantity,
        SUM(f.total_cost)                                              AS daily_cost,
        AVG(SUM(f.total_cost)) OVER (
            ORDER BY f.usage_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        )                                                              AS rolling_30_day_avg_cost,
        AVG(SUM(f.total_cost)) OVER (
            ORDER BY f.usage_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        )                                                              AS rolling_7_day_avg_cost
    FROM {target_catalog}.{SCHEMA}.gold_fact_usage f
    GROUP BY f.usage_date
    ORDER BY f.usage_date
""")

# COMMAND ----------

# DBTITLE 1,Gold Assets Permissions & Tags


# COMMAND ----------

# MAGIC %md
# MAGIC ## Cell 24 - Gold Assets Permissions & Tags

# COMMAND ----------

# ── View ownership (always — not prod-only) ───────────────────────────────────
spark.sql(f"ALTER VIEW {target_catalog}.{SCHEMA}.gold_top_cost_objects_current SET OWNER TO `{OWNER}`")
spark.sql(f"ALTER VIEW {target_catalog}.{SCHEMA}.gold_daily_spend_trend SET OWNER TO `{OWNER}`")

# ── Tables ────────────────────────────────────────────────────────────────────
if environment == "prod":
    gold_tables = [
        "gold_dim_workspace",
        "gold_dim_sku",
        "gold_dim_object",
        "gold_fact_usage",
    ]

    for table in gold_tables:
        full_name = f"{target_catalog}.{SCHEMA}.{table}"

        # Tags
        spark.sql(f"SET TAG ON TABLE {full_name} domain = data_and_automation")
        spark.sql(f"SET TAG ON TABLE {full_name} pipeline = databricks_analytics")

        # Permissions
        spark.sql(f"GRANT SELECT ON TABLE {full_name} TO `data_automation_gold_user`")
        spark.sql(f"GRANT SELECT ON TABLE {full_name} TO `data_automation_steward`")

    print(f"Tags and permissions applied to {len(gold_tables)} gold tables in {target_catalog}.{SCHEMA}")

else:
    print(f"Skipping table permissions and tags — environment is '{environment}', not 'prod'")

# ── View: gold_top_cost_objects_current ───────────────────────────────────────
if environment == "prod":
    view_name = f"{target_catalog}.{SCHEMA}.gold_top_cost_objects_current"

    spark.sql(f"SET TAG ON VIEW {view_name} domain = data_and_automation")
    spark.sql(f"SET TAG ON VIEW {view_name} pipeline = databricks_analytics")

    spark.sql(f"GRANT SELECT ON VIEW {view_name} TO `data_automation_gold_user`")
    spark.sql(f"GRANT SELECT ON VIEW {view_name} TO `data_automation_steward`")

    print(f"Tags and permissions applied to {view_name}")

else:
    print(f"Skipping view permissions — environment is '{environment}', not 'prod'")

# ── View: gold_daily_spend_trend ──────────────────────────────────────────────
if environment == "prod":
    view_name = f"{target_catalog}.{SCHEMA}.gold_daily_spend_trend"

    spark.sql(f"SET TAG ON VIEW {view_name} domain = data_and_automation")
    spark.sql(f"SET TAG ON VIEW {view_name} pipeline = databricks_analytics")

    spark.sql(f"GRANT SELECT ON VIEW {view_name} TO `data_automation_gold_user`")
    spark.sql(f"GRANT SELECT ON VIEW {view_name} TO `data_automation_steward`")

    print(f"Tags and permissions applied to {view_name}")

else:
    print(f"Skipping view permissions — environment is '{environment}', not 'prod'")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verification
# MAGIC Confirms every table exists and prints column count.
# MAGIC Runs regardless of initial_full_load value.

# COMMAND ----------

# ── Verification ──────────────────────────────────────────────────────────────
# Confirms every table and view exists and prints column count.
# Runs regardless of initial_full_load value.
# 8 silver tables + 4 gold tables + 2 gold views = 14 objects total.

tables = [
    # silver
    "silver_workspace_current",
    "silver_list_prices_history",
    "silver_usage_history",
    "silver_cluster_current",
    "silver_warehouse_current",
    "silver_job_current",
    "silver_pipeline_current",
    "silver_served_entity_current",
    "silver_query_history",
    # gold tables
    "gold_dim_workspace",
    "gold_dim_sku",
    "gold_dim_object",
    "gold_fact_usage",
    "gold_query_history",
    # gold views
    "gold_top_cost_objects_current",
    "gold_daily_spend_trend",
]

print(f"  {'Object':<40} {'Type':<8} {'Columns':<10} {'Status'}")
print(f"  {'-'*40} {'-'*8} {'-'*10} {'-'*10}")

VIEWS = {"gold_top_cost_objects_current", "gold_daily_spend_trend"}

all_ok = True
for tbl in tables:
    fqn  = f"{target_catalog}.{SCHEMA}.{tbl}"
    kind = "VIEW" if tbl in VIEWS else "TABLE"
    try:
        n_cols = len(spark.table(fqn).columns)
        print(f"  {tbl:<40} {kind:<8} {n_cols:<10} OK")
    except Exception as e:
        print(f"  {tbl:<40} {kind:<8} {'—':<10} NOT FOUND — {e}")
        all_ok = False

print()
print(f"  {'All 16 objects verified.' if all_ok else 'WARNING — one or more objects not found.'}")
