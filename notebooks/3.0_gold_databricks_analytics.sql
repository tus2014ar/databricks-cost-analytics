-- Databricks notebook source
-- DBTITLE 1,session variables
-- Tables built:
--   gold_dim_workspace
--   gold_dim_sku
--   gold_dim_object
--   gold_fact_usage
--
-- Views (created once in 1.0_table_setup.py — not rebuilt here):
--   gold_top_cost_objects_current
--   gold_daily_spend_trend

-- COMMAND ----------

-- DBTITLE 1,Cell 2
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

-- DBTITLE 1,gold_dim_workspace


-- COMMAND ----------

-- Gold: gold_dim_workspace
-- Source:  (dev_)data_automation.databricks_analytics.silver_workspace_current
-- Target:  (dev_)data_automation.databricks_analytics.gold_dim_workspace
-- Pattern: Full Overwrite

INSERT OVERWRITE IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_dim_workspace')
SELECT
    xxhash64(CAST(workspace_identifier AS STRING)) AS workspace_sk,
    workspace_identifier,
    workspace_name,
    workspace_url,
    workspace_status
FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_workspace_current');

-- COMMAND ----------

-- DBTITLE 1,gold_dim_sku


-- COMMAND ----------

-- Gold: gold_dim_sku
-- Source:  (dev_)data_automation.databricks_analytics.silver_list_prices_history
--          (dev_)data_automation.databricks_analytics.silver_usage_history
-- Target:  (dev_)data_automation.databricks_analytics.gold_dim_sku
-- Pattern: Full Overwrite

INSERT OVERWRITE IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_dim_sku')
WITH current_prices AS (
    SELECT
        sku_name,
        default_price AS current_price
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_list_prices_history')
    WHERE price_end_timestamp IS NULL
),
sku_products AS (
    SELECT
        sku_name,
        billing_origin_product,
        ROW_NUMBER() OVER (
            PARTITION BY sku_name
            ORDER BY COUNT(*) DESC
        ) AS rn
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE billing_origin_product IS NOT NULL
    GROUP BY sku_name, billing_origin_product
),
sku_base AS (
    SELECT DISTINCT sku_name
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_list_prices_history')
)
SELECT
    xxhash64(CAST(b.sku_name AS STRING))  AS sku_sk,
    b.sku_name,
    p.billing_origin_product,
    CAST(NULL AS STRING)                   AS product_family,
    c.current_price
FROM sku_base                              b
LEFT JOIN sku_products                     p ON b.sku_name = p.sku_name AND p.rn = 1
LEFT JOIN current_prices                   c ON b.sku_name = c.sku_name;

-- COMMAND ----------

-- DBTITLE 1,gold_dim_object


-- COMMAND ----------

-- DBTITLE 1,Cell 8
-- Gold: gold_dim_object
-- Source:  silver_usage_history + silver_cluster_current + silver_warehouse_current
--          silver_job_current + silver_pipeline_current + silver_served_entity_current
-- Target:  (dev_)data_automation.databricks_analytics.gold_dim_object
-- Pattern: Full Overwrite

INSERT OVERWRITE IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_dim_object')
WITH all_objects AS (
    SELECT DISTINCT
        cluster_identifier    AS object_identifier,
        'CLUSTER'             AS object_type,
        workspace_identifier
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE cluster_identifier IS NOT NULL

    UNION

    SELECT DISTINCT
        warehouse_identifier  AS object_identifier,
        'WAREHOUSE'           AS object_type,
        workspace_identifier
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE warehouse_identifier IS NOT NULL

    UNION

    SELECT DISTINCT
        job_identifier        AS object_identifier,
        'JOB'                 AS object_type,
        workspace_identifier
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE job_identifier IS NOT NULL

    UNION

    SELECT DISTINCT
        declarative_pipeline_identifier AS object_identifier,
        'PIPELINE'                      AS object_type,
        workspace_identifier
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE declarative_pipeline_identifier IS NOT NULL

    UNION

    SELECT DISTINCT
        endpoint_identifier   AS object_identifier,
        'ENDPOINT'            AS object_type,
        workspace_identifier
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE endpoint_identifier IS NOT NULL

    UNION                                                           -- ← ADD

    SELECT DISTINCT
        app_name              AS object_identifier,
        'APP'                 AS object_type,
        workspace_identifier
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE app_name IS NOT NULL                                      -- ← ADD
),
last_activity AS (
    SELECT
        cluster_identifier                                          AS object_identifier,
        'CLUSTER'                                                   AS object_type,
        MAX(usage_date)                                             AS last_activity_date,
        MAX_BY(executed_by_identity, usage_start_timestamp)        AS executed_by_identity
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE cluster_identifier IS NOT NULL
    GROUP BY cluster_identifier

    UNION ALL

    SELECT
        warehouse_identifier,
        'WAREHOUSE',
        MAX(usage_date),
        MAX_BY(executed_by_identity, usage_start_timestamp)
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE warehouse_identifier IS NOT NULL
    GROUP BY warehouse_identifier

    UNION ALL

    SELECT
        job_identifier,
        'JOB',
        MAX(usage_date),
        MAX_BY(executed_by_identity, usage_start_timestamp)
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE job_identifier IS NOT NULL
    GROUP BY job_identifier

    UNION ALL

    SELECT
        declarative_pipeline_identifier,
        'PIPELINE',
        MAX(usage_date),
        MAX_BY(executed_by_identity, usage_start_timestamp)
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE declarative_pipeline_identifier IS NOT NULL
    GROUP BY declarative_pipeline_identifier

    UNION ALL

    SELECT
        endpoint_identifier,
        'ENDPOINT',
        MAX(usage_date),
        MAX_BY(executed_by_identity, usage_start_timestamp)
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE endpoint_identifier IS NOT NULL
    GROUP BY endpoint_identifier

    UNION ALL                                                       -- ← ADD

    SELECT
        app_name,
        'APP',
        MAX(usage_date),
        MAX_BY(executed_by_identity, usage_start_timestamp)
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE app_name IS NOT NULL
    GROUP BY app_name                                               -- ← ADD
)
SELECT
    xxhash64(
        CAST(o.object_identifier AS STRING) || '||' ||
        CAST(o.object_type       AS STRING)
    )                                                               AS object_sk,
    o.object_identifier,
    o.object_type,
    COALESCE(
        c.cluster_name,
        w.warehouse_name,
        j.job_name,
        p.pipeline_name,
        e.endpoint_name,
        o.object_identifier                                         -- ← ADD: APP has no metadata table — use app_name directly
    )                                                               AS object_name,
    COALESCE(
        la.executed_by_identity,
        p.creator_email,
        j.creator_identity,
        c.owner_email
    )                                                               AS owner_identity,
    CASE
        WHEN la.executed_by_identity IS NOT NULL THEN 'executed_by_identity'
        WHEN p.creator_email         IS NOT NULL THEN 'creator_email'
        WHEN j.creator_identity      IS NOT NULL THEN 'creator_identity'
        WHEN c.owner_email           IS NOT NULL THEN 'owner_email'
        ELSE 'UNRESOLVED'
    END                                                             AS attribution_method,
    xxhash64(CAST(o.workspace_identifier AS STRING))               AS workspace_sk,
    la.last_activity_date,
    DATEDIFF(CURRENT_DATE(), la.last_activity_date)                 AS idle_day_count,
    CASE
        WHEN c.cluster_identifier        IS NULL
         AND w.warehouse_identifier      IS NULL
         AND j.job_identifier            IS NULL
         AND p.pipeline_identifier       IS NULL
         AND e.served_entity_identifier  IS NULL
        THEN TRUE
        ELSE FALSE
    END                                                             AS deleted_indicator
FROM all_objects                                                    o
LEFT JOIN last_activity                                             la
    ON  o.object_identifier = la.object_identifier
    AND o.object_type       = la.object_type
LEFT JOIN IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_cluster_current')       c
    ON  o.object_identifier = c.cluster_identifier
    AND o.object_type       = 'CLUSTER'
LEFT JOIN IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_warehouse_current')     w
    ON  o.object_identifier = w.warehouse_identifier
    AND o.object_type       = 'WAREHOUSE'
LEFT JOIN IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_job_current')           j
    ON  o.object_identifier = j.job_identifier
    AND o.object_type       = 'JOB'
LEFT JOIN IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_pipeline_current')      p
    ON  o.object_identifier = p.pipeline_identifier
    AND o.object_type       = 'PIPELINE'
LEFT JOIN IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_served_entity_current') e
    ON  o.object_identifier = e.served_entity_identifier
    AND o.object_type       = 'ENDPOINT';
    -- NOTE: APP objects have no metadata table in system tables.
    -- object_name falls back to app_name (object_identifier) directly.
    -- owner_identity and attribution_method will be UNRESOLVED for APP objects.

-- COMMAND ----------

-- DBTITLE 1,gold_query_history
-- Gold: gold_query_history — Step 1 DELETE
-- Source:  (dev_)data_automation.databricks_analytics.silver_query_history
-- Target:  (dev_)data_automation.databricks_analytics.gold_query_history
-- Pattern: DELETE + INSERT (partition-selective on query_start_hour)
-- Filter:  execution_status = 'FINISHED' only
--          FAILED = 0.01% of total task seconds (9.6s across 1,151 queries) — negligible
--          CANCELED = 0 observed in Claude query history

DELETE FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_query_history')
WHERE query_start_hour IN (
    SELECT DISTINCT query_start_hour
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_query_history')
    WHERE query_start_hour >= (
        SELECT COALESCE(MAX(query_start_hour), CAST('1900-01-01' AS TIMESTAMP))
        FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_query_history')
    )
);

-- COMMAND ----------

-- DBTITLE 1,gold_query_history
-- Gold: gold_query_history — Step 2 INSERT
-- Loads FINISHED queries only from silver_query_history
-- Denormalizes warehouse_name from silver_warehouse_current
-- Denormalizes workspace_name from silver_workspace_current
-- Claude queries identified in dashboard via:
--   client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')

INSERT INTO IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_query_history')
WITH new_hours AS (
    SELECT DISTINCT query_start_hour
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_query_history')
    WHERE query_start_hour >= (
        SELECT COALESCE(MAX(query_start_hour), CAST('1900-01-01' AS TIMESTAMP))
        FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_query_history')
    )
)
SELECT
    q.query_identifier,
    q.workspace_identifier,
    ws.workspace_name,
    q.executed_by_identity,
    q.warehouse_identifier,
    w.warehouse_name,
    q.client_application,
    q.client_driver,
    q.execution_status,
    q.statement_type,
    q.result_cache_hit_indicator,
    q.start_timestamp,
    q.end_timestamp,
    q.query_start_hour,
    q.query_start_date,
    q.total_duration_ms,
    q.waiting_for_compute_duration_ms,
    q.waiting_at_capacity_duration_ms,
    q.compilation_duration_ms,
    q.execution_duration_ms,
    q.total_task_duration_ms,
    q.result_fetch_duration_ms,
    q.read_rows,
    q.produced_rows,
    q.read_bytes,
    q.session_identifier
FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_query_history') q
JOIN new_hours nh
    ON q.query_start_hour = nh.query_start_hour
LEFT JOIN IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_warehouse_current') w
    ON q.warehouse_identifier = w.warehouse_identifier
LEFT JOIN IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_workspace_current') ws
    ON q.workspace_identifier = ws.workspace_identifier
WHERE q.execution_status = 'FINISHED';

-- COMMAND ----------

-- DBTITLE 1,gold_fact_usage - delete


-- COMMAND ----------

-- Gold: gold_fact_usage — Step 1 DELETE
-- Source:  (dev_)data_automation.databricks_analytics.silver_usage_history
-- Target:  (dev_)data_automation.databricks_analytics.gold_fact_usage
-- Pattern: DELETE + INSERT (Partition-selective)
-- Removes all gold rows for usage_hours present in today's new silver window
-- Only touches partitions in the daily watermark window
-- Historical partitions outside this window are never touched

DELETE FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_fact_usage')
WHERE usage_hour IN (
    SELECT DISTINCT usage_hour
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE usage_hour >= (                                           -- ← > to >=
        SELECT COALESCE(MAX(usage_hour), CAST('1900-01-01' AS TIMESTAMP))
        FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_fact_usage')
    )
);

-- COMMAND ----------

-- DBTITLE 1,gold_fact_usage- Insert
-- Gold: gold_fact_usage — Step 2 INSERT
-- Re-aggregates silver for exactly the same hours deleted in Step 1
-- No duplicates — DELETE already cleared those hours
-- Grain: One row per workspace_sk x object_sk x sku_sk x usage_hour
-- fact_sk: surrogate PK — xxhash64 of full grain with COALESCE sentinels

INSERT INTO IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_fact_usage')
WITH new_hours AS (
    SELECT DISTINCT usage_hour
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE usage_hour >= (
        SELECT COALESCE(MAX(usage_hour), CAST('1900-01-01' AS TIMESTAMP))
        FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_fact_usage')
    )
),
silver_new AS (
    SELECT
        usage_hour,
        usage_date,
        workspace_identifier,
        sku_name,
        usage_quantity,
        billing_origin_product,
        tag_team_text,
        tag_domain_text,
        tag_purpose_text,
        usage_start_timestamp,
        cluster_identifier,
        warehouse_identifier,
        job_identifier,
        declarative_pipeline_identifier,
        endpoint_identifier,
        app_name,
        record_identifier
    FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_usage_history')
    WHERE usage_hour IN (SELECT usage_hour FROM new_hours)
),
price_join AS (
    SELECT
        s.record_identifier,
        s.usage_hour,
        s.usage_date,
        s.workspace_identifier,
        s.sku_name,
        s.usage_quantity,
        s.billing_origin_product,
        s.tag_team_text,
        s.tag_domain_text,
        s.tag_purpose_text,
        CAST(
            s.usage_quantity * p.default_price
        AS DECIMAL(18, 2))                                          AS usage_cost,
        COALESCE(
            s.cluster_identifier,
            s.warehouse_identifier,
            s.job_identifier,
            s.declarative_pipeline_identifier,
            s.endpoint_identifier,
            s.app_name
        )                                                           AS object_identifier,
        CASE
            WHEN s.cluster_identifier              IS NOT NULL THEN 'CLUSTER'
            WHEN s.warehouse_identifier            IS NOT NULL THEN 'WAREHOUSE'
            WHEN s.job_identifier                  IS NOT NULL THEN 'JOB'
            WHEN s.declarative_pipeline_identifier IS NOT NULL THEN 'PIPELINE'
            WHEN s.endpoint_identifier             IS NOT NULL THEN 'ENDPOINT'
            WHEN s.app_name                        IS NOT NULL THEN 'APP'
            ELSE 'UNRESOLVED'
        END                                                         AS object_type
    FROM silver_new                                                 s
    LEFT JOIN IDENTIFIER(:prefix || 'data_automation.databricks_analytics.silver_list_prices_history') p
        ON  s.sku_name              = p.sku_name
        AND s.usage_start_timestamp BETWEEN p.price_start_timestamp
                                    AND COALESCE(p.price_end_timestamp, CURRENT_TIMESTAMP())
)
SELECT
    xxhash64(                                                       -- ← ADD fact_sk
        CAST(f.usage_hour                          AS STRING) || '||' ||
        CAST(COALESCE(w.workspace_sk,          -1) AS STRING) || '||' ||
        CAST(COALESCE(o.object_sk,             -1) AS STRING) || '||' ||
        CAST(s.sku_sk                              AS STRING) || '||' ||
        CAST(COALESCE(f.tag_team_text,    'UNTAGGED') AS STRING) || '||' ||
        CAST(COALESCE(f.tag_domain_text,  'UNTAGGED') AS STRING) || '||' ||
        CAST(COALESCE(f.tag_purpose_text, 'UNTAGGED') AS STRING)
    )                                                               AS fact_sk,
    f.usage_hour,
    f.usage_date,
    w.workspace_sk,
    o.object_sk,
    s.sku_sk,
    COALESCE(f.tag_team_text,   'UNTAGGED')                         AS tag_team_text,
    COALESCE(f.tag_domain_text, 'UNTAGGED')                         AS tag_domain_text,
    COALESCE(f.tag_purpose_text,'UNTAGGED')                         AS tag_purpose_text,
    CAST(SUM(f.usage_cost)          AS DECIMAL(18, 2))              AS total_cost,
    CAST(SUM(f.usage_quantity)      AS DECIMAL(18, 6))              AS total_usage_quantity,
    COUNT(*)                                                         AS billing_row_count
FROM price_join                                                      f
LEFT JOIN IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_dim_workspace') w
    ON  f.workspace_identifier = w.workspace_identifier
LEFT JOIN IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_dim_object')    o
    ON  f.object_identifier    = o.object_identifier
    AND f.object_type          = o.object_type
LEFT JOIN IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_dim_sku')       s
    ON  f.sku_name             = s.sku_name
GROUP BY
    f.usage_hour,
    f.usage_date,
    w.workspace_sk,
    o.object_sk,
    s.sku_sk,
    f.tag_team_text,
    f.tag_domain_text,
    f.tag_purpose_text;

-- COMMAND ----------

-- DBTITLE 1,dedup safeguard


-- COMMAND ----------

-- gold_fact_usage -- Post-INSERT dedup safeguard
-- Removes duplicate fact_sk rows introduced by repeated pipeline runs
-- or late-arriving boundary hour data.
-- Scoped to last 48 hours only -- avoids full table scan.
-- No-op when no duplicates exist -- safe to run on every execution.

DELETE FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_fact_usage')
WHERE fact_sk IN (
    SELECT fact_sk
    FROM (
        SELECT
            fact_sk,
            ROW_NUMBER() OVER (PARTITION BY fact_sk ORDER BY fact_sk) AS rn
        FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_fact_usage')
        WHERE usage_hour >= (
            SELECT COALESCE(
                DATEADD(HOUR, -48, MAX(usage_hour)),
                CAST('1900-01-01' AS TIMESTAMP)
            )
            FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_fact_usage')
        )
    )
    WHERE rn > 1
);

-- COMMAND ----------

-- DBTITLE 1,Verification


-- COMMAND ----------



-- COMMAND ----------

-- Verification -- row counts per gold table and view
-- Runs on every execution
-- Any 0 row count on dim or fact tables indicates a load issue
-- Views always return rows as long as fact table is populated

SELECT 'gold_dim_workspace'             AS table_name, COUNT(*) AS row_count FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_dim_workspace')
UNION ALL
SELECT 'gold_dim_sku',                                 COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_dim_sku')
UNION ALL
SELECT 'gold_dim_object',                              COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_dim_object')
UNION ALL
SELECT 'gold_fact_usage',                              COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_fact_usage')
UNION ALL
SELECT 'gold_query_history',                           COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_query_history')
UNION ALL
SELECT 'gold_top_cost_objects_current',                COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_top_cost_objects_current')
UNION ALL
SELECT 'gold_daily_spend_trend',                       COUNT(*) FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_daily_spend_trend')
ORDER BY table_name;

-- Duplicate check -- fact_sk must be 100% unique after every run
SELECT
    COUNT(*)                           AS total_rows,
    COUNT(DISTINCT fact_sk)            AS distinct_fact_sk,
    COUNT(*) - COUNT(DISTINCT fact_sk) AS duplicates,
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT fact_sk) THEN 'PASS'
        ELSE 'FAIL'
    END                                AS status
FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_fact_usage');

-- Duplicate check — gold_query_history query_identifier must be 100% unique
SELECT
    COUNT(*)                                        AS total_rows,
    COUNT(DISTINCT query_identifier)                AS distinct_query_identifier,
    COUNT(*) - COUNT(DISTINCT query_identifier)     AS duplicates,
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT query_identifier) THEN 'PASS'
        ELSE 'FAIL'
    END                                             AS status
FROM IDENTIFIER(:prefix || 'data_automation.databricks_analytics.gold_query_history');
