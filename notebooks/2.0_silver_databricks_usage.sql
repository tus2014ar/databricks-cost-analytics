-- Databricks notebook source
-- DBTITLE 1,Session variables
-- 2.0 Silver — Databricks Cost Analytics
-- Loads all 8 silver tables from Databricks system tables.
-- Runtime: Serverless Warehouse — Unity Catalog Enabled
--
-- Tables loaded:
--   silver_list_prices_history
--   silver_usage_history
--   silver_workspace_current
--   silver_cluster_current
--   silver_warehouse_current
--   silver_job_current
--   silver_pipeline_current
--   silver_served_entity_current

-- COMMAND ----------

-- STEP 1: Declare session variables
DECLARE OR REPLACE VARIABLE environment STRING;
DECLARE OR REPLACE VARIABLE prefix      STRING;

SET VAR environment = LOWER(TRIM(:environment));

-- Fail immediately if environment is misconfigured before any INSERT runs
SELECT assert_true(
    environment IN ('dev', 'prod'),
    'Invalid environment. Use ''dev'' or ''prod''.'
);

-- dev  → 'dev_'  → targets dev_data_automation.databricks_analytics
-- prod → ''      → targets data_automation.databricks_analytics
SET VAR prefix = CASE WHEN environment = 'prod' THEN '' ELSE 'dev_' END;

-- COMMAND ----------

-- DBTITLE 1,silver_list_prices_history


-- COMMAND ----------

-- DBTITLE 1,Cell 4
-- Silver: silver_list_prices_history
-- Source:  system.billing.list_prices
-- Target:  (dev_)data_automation.databricks_analytics.silver_list_prices_history
-- Pattern: INSERT OVERWRITE — full refresh every run
-- Grain:   One row per SKU per price effective period
-- PK:      sku_name + price_start_timestamp
-- pricing.default used — published standard list price per Databricks documentation

INSERT OVERWRITE IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_list_prices_history')
SELECT
    sku_name,
    price_start_time                        AS price_start_timestamp,
    price_end_time                          AS price_end_timestamp,
    cloud,
    currency_code,
    usage_unit,
    CAST(pricing.`default` AS DECIMAL(18, 8)) AS default_price,
    TO_JSON(pricing)                        AS pricing_json
FROM system.billing.list_prices;

-- COMMAND ----------

-- DBTITLE 1,silver_usage_history


-- COMMAND ----------

-- DBTITLE 1,Cell 6
-- Silver: silver_usage_history
-- Source:  system.billing.usage
-- Target:  (dev_)data_automation.databricks_analytics.silver_usage_history

INSERT INTO IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
WITH watermark AS (
    SELECT COALESCE(
        MAX(usage_start_timestamp),
        CAST('1900-01-01T00:00:00' AS TIMESTAMP)
    ) AS max_ts
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
)
SELECT
    record_id                                                    AS record_identifier,
    account_id                                                   AS account_identifier,
    workspace_id                                                 AS workspace_identifier,
    sku_name,
    cloud,
    usage_date,
    DATE_TRUNC('HOUR', usage_start_time)                         AS usage_hour,
    usage_start_time                                             AS usage_start_timestamp,
    usage_end_time                                               AS usage_end_timestamp,
    CAST(usage_quantity AS DECIMAL(18, 6))                       AS usage_quantity,
    usage_unit,
    billing_origin_product,
    usage_type,
    record_type,
    usage_metadata.cluster_id                                    AS cluster_identifier,
    usage_metadata.warehouse_id                                  AS warehouse_identifier,
    usage_metadata.job_id                                        AS job_identifier,
    usage_metadata.dlt_pipeline_id                               AS declarative_pipeline_identifier,
    usage_metadata.endpoint_id                                   AS endpoint_identifier,
    usage_metadata.app_name                                      AS app_name,             -- ← ADD
    usage_metadata.job_name                                      AS job_name,
    identity_metadata.run_as                                     AS executed_by_identity,
    CASE
        WHEN TRIM(LOWER(custom_tags['team']))   IN ('n/a','na','null','none','#n/a','-','--')
        THEN NULL
        ELSE NULLIF(TRIM(custom_tags['team']),   '')
    END                                                          AS tag_team_text,
    CASE
        WHEN TRIM(LOWER(custom_tags['domain'])) IN ('n/a','na','null','none','#n/a','-','--')
        THEN NULL
        ELSE NULLIF(TRIM(custom_tags['domain']), '')
    END                                                          AS tag_domain_text,
    CASE
        WHEN TRIM(LOWER(custom_tags['purpose'])) IN ('n/a','na','null','none','#n/a','-','--')
        THEN NULL
        ELSE NULLIF(TRIM(custom_tags['purpose']), '')
    END                                                          AS tag_purpose_text,
    custom_tags
FROM system.billing.usage, watermark
WHERE usage_start_time > watermark.max_ts;

-- COMMAND ----------

-- DBTITLE 1,silver_workspace_current


-- COMMAND ----------

-- DBTITLE 1,Cell 8


-- COMMAND ----------

-- Silver: silver_workspace_current
-- Source:  system.access.workspaces_latest
-- Target:  (dev_)data_automation.databricks_analytics.silver_workspace_current
-- Pattern: Full Overwrite — source is latest state only, no history retained

INSERT OVERWRITE IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_workspace_current')
SELECT
    workspace_id    AS workspace_identifier,
    account_id      AS account_identifier,
    workspace_name  AS workspace_name,
    workspace_url,
    create_time     AS workspace_creation_timestamp,
    status          AS workspace_status
FROM system.access.workspaces_latest;

-- COMMAND ----------

-- Silver: silver_cluster_current
-- Source:  system.compute.clusters
-- Target:  (dev_)data_automation.databricks_analytics.silver_cluster_current
-- Pattern: Full Overwrite with ROW_NUMBER() Deduplication

INSERT OVERWRITE IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_cluster_current')
SELECT
    cluster_id                                              AS cluster_identifier,
    workspace_id                                            AS workspace_identifier,
    cluster_name                                            AS cluster_name,
    owned_by                                                AS owner_email,
    create_time                                             AS create_timestamp,
    delete_time                                             AS delete_timestamp,
    driver_node_type,
    worker_node_type,
    worker_count                                            AS worker_count,
    min_autoscale_workers                                   AS autoscale_min_workers,
    max_autoscale_workers                                   AS autoscale_max_workers,
    auto_termination_minutes                                AS autotermination_minutes,
    enable_elastic_disk                                     AS elastic_disk_enabled_indicator,
    tags                                                    AS custom_tags,
    cluster_source,
    dbr_version                                             AS runtime_version,
    change_time                                             AS change_timestamp,
    (delete_time IS NOT NULL)                               AS deleted_indicator
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY cluster_id ORDER BY change_time DESC) AS rn
    FROM system.compute.clusters
)
WHERE rn = 1;

-- COMMAND ----------

-- DBTITLE 1,silver_warehouse_current


-- COMMAND ----------

-- DBTITLE 1,Cell 12
-- Silver: silver_warehouse_current
-- Source:  system.compute.warehouses
-- Target:  (dev_)data_automation.databricks_analytics.silver_warehouse_current
-- Pattern: Full Overwrite with ROW_NUMBER() Deduplication

INSERT OVERWRITE IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_warehouse_current')
SELECT
    warehouse_id                                            AS warehouse_identifier,
    workspace_id                                            AS workspace_identifier,
    warehouse_name                                           AS warehouse_name,
    warehouse_type,
    warehouse_channel                                        AS warehouse_channel,
    warehouse_size                                           AS warehouse_size,
    min_clusters                                            AS min_cluster_count,
    max_clusters                                            AS max_cluster_count,
    auto_stop_minutes                                       AS auto_stop_minutes,
    created_by                                              AS creator_identity,
    tags                                                    AS custom_tags,
    change_time                                             AS change_timestamp,
    delete_time                                             AS delete_timestamp,
    (delete_time IS NOT NULL)                               AS deleted_indicator
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY warehouse_id ORDER BY change_time DESC) AS rn
    FROM system.compute.warehouses
)
WHERE rn = 1;

-- COMMAND ----------

-- DBTITLE 1,silver_job_current


-- COMMAND ----------

-- Silver: silver_job_current
-- Source:  system.lakeflow.jobs
-- Target:  (dev_)data_automation.databricks_analytics.silver_job_current
-- Pattern: Full Overwrite with ROW_NUMBER() Deduplication

INSERT OVERWRITE IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_job_current')
SELECT
    job_id                                                  AS job_identifier,
    workspace_id                                            AS workspace_identifier,
    name                                                    AS job_name,
    creator_id                                              AS creator_identifier,
    creator_user_name                                       AS creator_identity,
    run_as                                                  AS run_as_identifier,
    run_as_user_name                                        AS run_as_identity,
    description                                             AS job_description,
    trigger_type,
    paused                                                  AS paused_indicator,
    change_time                                             AS change_timestamp,
    create_time                                             AS create_timestamp,
    delete_time                                             AS delete_timestamp,
    tags                                                    AS custom_tags,
    (delete_time IS NOT NULL)                               AS deleted_indicator
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY job_id ORDER BY change_time DESC) AS rn
    FROM system.lakeflow.jobs
)
WHERE rn = 1;

-- COMMAND ----------

-- DBTITLE 1,silver_pipeline_current


-- COMMAND ----------

-- Silver: silver_pipeline_current
-- Source:  system.lakeflow.pipelines
-- Target:  (dev_)data_automation.databricks_analytics.silver_pipeline_current
-- Pattern: Full Overwrite with ROW_NUMBER() Deduplication

INSERT OVERWRITE IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_pipeline_current')
SELECT
    pipeline_id                                             AS pipeline_identifier,
    workspace_id                                            AS workspace_identifier,
    name                                                    AS pipeline_name,
    pipeline_type,
    created_by                                              AS creator_email,
    run_as                                                  AS run_as_email,
    tags                                                    AS custom_tags,
    TO_JSON(settings)                                       AS settings_json,
    TO_JSON(configuration)                                  AS configuration_json,
    change_time                                             AS change_timestamp,
    create_time                                             AS create_timestamp,
    delete_time                                             AS delete_timestamp,
    (delete_time IS NOT NULL)                               AS deleted_indicator
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY pipeline_id ORDER BY change_time DESC) AS rn
    FROM system.lakeflow.pipelines
)
WHERE rn = 1;

-- COMMAND ----------

-- DBTITLE 1,silver_served_entity_current


-- COMMAND ----------

-- Silver: silver_served_entity_current
-- Source:  system.serving.served_entities
-- Target:  (dev_)data_automation.databricks_analytics.silver_served_entity_current
-- Pattern: Full Overwrite with ROW_NUMBER() Deduplication

INSERT OVERWRITE IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_served_entity_current')
SELECT
    served_entity_id                                        AS served_entity_identifier,
    workspace_id                                            AS workspace_identifier,
    endpoint_id                                             AS endpoint_identifier,
    endpoint_name                                           AS endpoint_name,
    served_entity_name                                      AS served_entity_name,
    entity_type,
    entity_name                                             AS entity_name,
    CAST(entity_version AS STRING)                          AS entity_version,
    endpoint_config_version,
    task,
    created_by                                              AS creator_identity,
    TO_JSON(custom_model_config)                            AS custom_model_config_json,
    TO_JSON(foundation_model_config)                        AS foundation_model_config_json,
    change_time                                             AS change_timestamp,
    endpoint_delete_time                                    AS delete_timestamp,
    (endpoint_delete_time IS NOT NULL)                      AS deleted_indicator
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY served_entity_id ORDER BY change_time DESC) AS rn
    FROM system.serving.served_entities
)
WHERE rn = 1;

-- COMMAND ----------

-- DBTITLE 1,silver_query_history
-- Silver: silver_query_history
-- Source:  system.query.history
-- Target:  (dev_)data_automation.databricks_analytics.silver_query_history
-- Pattern: Append with Watermark on start_timestamp
-- Grain:   One row per query execution — all execution statuses retained

INSERT INTO IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_query_history')
WITH watermark AS (
    SELECT COALESCE(
        MAX(start_timestamp),
        CAST('1900-01-01T00:00:00' AS TIMESTAMP)
    ) AS max_ts
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_query_history')
)
SELECT
    statement_id AS query_identifier,
    workspace_id                                        AS workspace_identifier,
    executed_by                                         AS executed_by_identity,
    compute.warehouse_id                                AS warehouse_identifier,
    client_application,
    client_driver,
    execution_status,
    statement_type,
    from_result_cache                                   AS result_cache_hit_indicator,
    start_time                                          AS start_timestamp,
    end_time                                            AS end_timestamp,
    DATE_TRUNC('HOUR', start_time)                      AS query_start_hour,
    DATE(start_time)                                    AS query_start_date,
    total_duration_ms,
    waiting_for_compute_duration_ms,
    waiting_at_capacity_duration_ms,
    compilation_duration_ms,
    execution_duration_ms,
    total_task_duration_ms,
    result_fetch_duration_ms,
    read_rows,
    produced_rows,
    read_bytes,
    session_id                                          AS session_identifier
FROM system.query.history, watermark
WHERE start_time > watermark.max_ts;

-- COMMAND ----------

-- DBTITLE 1,Verification


-- COMMAND ----------

-- Verification — row counts per silver table
-- Runs on every execution
-- Any 0 row count indicates a load issue
-- silver_usage_history expected to grow daily — check count > 0

SELECT 'silver_list_prices_history'    AS table_name, COUNT(*) AS row_count FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_list_prices_history')
UNION ALL
SELECT 'silver_usage_history',                        COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
UNION ALL
SELECT 'silver_workspace_current',                    COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_workspace_current')
UNION ALL
SELECT 'silver_cluster_current',                      COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_cluster_current')
UNION ALL
SELECT 'silver_warehouse_current',                    COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_warehouse_current')
UNION ALL
SELECT 'silver_job_current',                          COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_job_current')
UNION ALL
SELECT 'silver_pipeline_current',                     COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_pipeline_current')
UNION ALL
SELECT 'silver_served_entity_current',                COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_served_entity_current')
UNION ALL
SELECT 'silver_query_history',                        COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_query_history')
ORDER BY table_name;
