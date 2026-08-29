# Databricks Cost Analytics Pipeline

**Domain:** data_automation
**Schema:** databricks_analytics
**Author:** Tushar — Data + Automation Team
**Reviewer:** Data + Automation Team
**Last updated:** June 2026

---

## Overview

Centralises Databricks platform cost data from Unity Catalog system tables into a queryable star schema. Surfaces spend by workspace, SKU, and billable object with owner attribution and idle resource detection. Includes Claude query cost attribution via pro-rata task time weighting. Powers the Databricks Cost Analytics dashboard.

**Business questions answered:**

| # | Question |
| --- | --- |
| BQ1 | Total spend by workspace, product, and SKU |
| BQ2 | Daily spend trend with 7-day and 30-day rolling averages |
| BQ3 | Top cost objects by lifetime spend |
| BQ4 | Object ownership, attribution method, and idle status |
| BQ5 | Spend by tag — team, domain, purpose |
| BQ6 | Attribution coverage — how much spend is attributed vs UNRESOLVED |
| BQ7 | Total Claude estimated attributed cost by month and warehouse |
| BQ8 | Claude cost by user — cost-per-query and active days |
| BQ9 | Query volume, failure rate, and cache hit rate by tool |
| BQ10 | Claude cost vs total platform spend |

---

## Architecture

No bronze layer. Source data is read directly from Databricks Unity Catalog system tables. Silver tables normalise and flatten source structs. Gold tables build a star schema for BI consumption.

```
system.billing.usage              system.billing.list_prices
system.compute.clusters           system.compute.warehouses
system.lakeflow.jobs              system.lakeflow.pipelines
system.access.workspaces_latest   system.serving.served_entities
system.query.history                                              ← NEW
                          │
                          ▼  Silver (9 tables)
         (dev_)data_automation.databricks_analytics
                          │
                          ▼  Gold (5 tables + 2 views)
         (dev_)data_automation.databricks_analytics
```

---

## Silver Tables

| Table | Source | Pattern | Grain |
| --- | --- | --- | --- |
| `silver_list_prices_history` | `system.billing.list_prices` | Full Overwrite | One row per SKU per price effective period |
| `silver_usage_history` | `system.billing.usage` | Append with Watermark | One row per billing usage record |
| `silver_workspace_current` | `system.access.workspaces_latest` | Full Overwrite | One row per workspace (current state) |
| `silver_cluster_current` | `system.compute.clusters` | Full Overwrite + ROW_NUMBER() | One row per cluster (current configuration) |
| `silver_warehouse_current` | `system.compute.warehouses` | Full Overwrite + ROW_NUMBER() | One row per SQL warehouse (current configuration) |
| `silver_job_current` | `system.lakeflow.jobs` | Full Overwrite + ROW_NUMBER() | One row per job (current configuration) |
| `silver_pipeline_current` | `system.lakeflow.pipelines` | Full Overwrite + ROW_NUMBER() | One row per DLT pipeline (current configuration) |
| `silver_served_entity_current` | `system.serving.served_entities` | Full Overwrite + ROW_NUMBER() | One row per model serving endpoint entity |
| `silver_query_history` | `system.query.history` | Append with Watermark | One row per query execution — all statuses retained |

---

## Gold Objects

| Object | Type | Pattern | Grain |
| --- | --- | --- | --- |
| `gold_dim_workspace` | Dimension | Full Overwrite | One row per workspace |
| `gold_dim_sku` | Dimension | Full Overwrite | One row per SKU |
| `gold_dim_object` | Dimension | Full Overwrite | One row per billable object (current state) |
| `gold_fact_usage` | Fact | DELETE + INSERT (Partition-selective) | One row per workspace × object × SKU × hour |
| `gold_query_history` | Fact | DELETE + INSERT (Partition-selective) | One row per FINISHED query execution |
| `gold_top_cost_objects_current` | View | No load — always current | All-time spend per billable object with rank |
| `gold_daily_spend_trend` | View | No load — always current | Daily cost with 7-day and 30-day rolling averages |

---

## Repository Structure

```
docs/
├── ARCHITECTURE.md          ← this file
├── table_designs.md         ← authoritative column definitions
├── load_patterns.md         ← load pattern decisions and EDA evidence
└── dashboard-reference.md   ← dashboard SQL reference
notebooks/
├── 1.0_table_setup.py
├── 2.0_silver_databricks_usage.sql
├── 3.0_gold_databricks_analytics.sql
├── init_libraries.py
├── dev_databricks_usage_analytics.yml   ← Databricks Asset Bundle job config
└── prod_databricks_usage_analytics.yml  ← Databricks Asset Bundle job config
```

---

## Getting Started

### Prerequisites

- Access to `dev_data_automation` catalog in the Databricks dev workspace
- Read access to Databricks system tables:
  - `system.billing` — usage and list prices
  - `system.compute` — clusters and warehouses
  - `system.lakeflow` — jobs and pipelines
  - `system.access` — workspaces
  - `system.serving` — served entities
  - `system.query` — query execution history (**NEW**)
- Serverless Warehouse — Unity Catalog Enabled (`warehouse_id: <WAREHOUSE_ID>`)

### First run — table setup

On the first run only, set `initial_full_load = True` to create all tables and schema.

Deploy the bundle:

```bash
databricks bundle deploy --target dev
```

Then in Databricks UI — **Workflows → dev_databricks_analytics → Run now with different parameters** — set `initial_full_load = True` and run.

All subsequent daily runs leave `initial_full_load = False`. The `table_setup_check` condition task gates the setup notebook and skips it automatically.

### Day-to-day runs

The dev job runs manually. The prod job runs daily at 6:00 AM America/Detroit (`pause_status: PAUSED` until end-to-end validation is complete — unpause after prod sign-off).

---

## Job Parameters

| Parameter | Dev default | Prod default | Description |
| --- | --- | --- | --- |
| `environment` | `dev` | `prod` | Controls catalog prefix — `dev_` for dev, empty for prod |
| `initial_full_load` | `False` | `False` | Set `True` on first run only to create tables |
| `verbose` | `False` | `False` | Set `True` temporarily for debug logging |

---

## Task Chain

```
table_setup_check  (condition task — evaluates initial_full_load == "True")
        │
        ├── true  →  table_setup              (1.0_table_setup.py — Serverless)
        │                   │
        └── false ──────────▼
                    silver_databricks_usage   (2.0_silver_databricks_usage.sql — Serverless Warehouse)
                            │
                            ▼
                    gold_databricks_analytics (3.0_gold_databricks_analytics.sql — Serverless Warehouse)
```

---

## Claude Cost Analytics Extension

Added June 2026. Extends the pipeline with query-level execution history from `system.query.history` to enable pro-rata Claude cost attribution.

**How it works:**

Claude queries are identified in `gold_query_history` by filtering `client_application`:

```sql
WHERE client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
```

Cost attribution uses a pro-rata formula applied at daily grain per warehouse in the dashboard layer:

```
Claude Estimated Cost (daily, per warehouse)
= Total Warehouse Cost (USD)
  × Claude Task Seconds (total_task_duration_ms)
  ÷ Total Warehouse Task Seconds
```

**Validated attributed cost:** $462.02 (Feb 11 – Jun 11, 2026) across 4 shared serverless warehouses.

**Key design decisions:**

| Decision | Approach |
| --- | --- |
| Claude identification | `client_application` filtered in dashboard — no derived boolean in pipeline |
| Attribution metric | `total_task_duration_ms` — true parallel compute, not wall-clock |
| Attribution grain | Daily per warehouse — monthly grain inflates results on shared warehouses |
| Silver status filter | All statuses retained (FINISHED, FAILED, CANCELED) |
| Gold status filter | FINISHED only — FAILED = 0.01% of task seconds (confirmed by profiling) |
| Partition key | `query_start_hour` (hourly) — forward-looking, aligns with `silver_usage_history` |
| Column naming | internal data naming standard v6.0 compliant |

**Approved documentation:** Claude Cost Analytics — Table Design and Load Pattern Proposal v10 FINAL.

---

## Design Decisions

All column-level design decisions are in `docs/table_designs.md`. All load pattern decisions are in `docs/load_patterns.md`. Claude cost analytics decisions are in `docs/claude_cost_table_designs.md`. Deviations from the Silver + Gold Modeling Reference are documented below.

| Decision | Rationale |
| --- | --- |
| No bronze layer | System tables are Unity Catalog native — no ingestion step needed |
| `silver_usage_history` watermark on `usage_start_timestamp` | Timestamp granularity is more precise than date — safer on pipeline failure recovery |
| Cost derived at `gold_fact_usage` load time via price join | Keeps silver and pricing concerns cleanly separated — no cost column at silver |
| `gold_dim_object` Full Overwrite | No ownership history tracking required — current owner only |
| `gold_fact_usage` hourly grain | Source is hourly per Databricks documentation — daily aggregation deferred to view |
| Rolling averages in `gold_daily_spend_trend` view | Pre-storing rolling averages on fact table would require Full Overwrite on partitioned table — view computes on demand at no storage cost |
| `billing_origin_product` sourced from `silver_usage_history` | `system.billing.list_prices` does not carry this field — resolved as most common value per SKU via ROW_NUMBER() |
| `_email` suffix retained only where 100% email confirmed | `_identity` suffix applied where live extract showed mixed values (UUIDs, System-User) |
| `pricing.default` used for cost calculation | Officially endorsed field per Databricks documentation and sample queries — promotional rates not applied by design |
| `gold_fact_usage` pattern — DELETE + INSERT | Works on Serverless Warehouse SQL notebook without Python or Spark config. Only touches partitions in the daily watermark window |
| `silver_query_history` watermark on `start_timestamp` | Same reasoning as `silver_usage_history` — millisecond precision, safe on failure recovery |
| `gold_query_history` partitioned by `query_start_hour` | Forward-looking — enables future intra-day analytics and hour-level joins to `silver_usage_history` |
| `statement_text` and `error_message` excluded from silver | Governance decision — may contain sensitive data or PII. Databricks redacts with customer-managed keys |
| `gold_query_history` FINISHED only | FAILED queries = 0.01% of total task seconds (9.6s across 1,151 queries) — negligible cost impact confirmed by profiling |
| Claude cost attribution in dashboard layer | Power BI is sole consumer — DAX measures are maintainable. Reduces pipeline complexity. Gold views can be added in future without schema changes |

---

## Open Items

| # | Item | Owner | Status |
| --- | --- | --- | --- |
| 01 | CANCELED query monitoring — zero CANCELED Claude queries observed to date. If CANCELED appears in future, profile `total_task_duration_ms` before updating gold filter | Data + Automation | Monitor |
| 02 | New Claude client strings — if Anthropic or Databricks introduces new MCP client strings, update dashboard filter `IN` clause | Data + Automation | Monitor |
| 03 | `system.query.history` retention — Databricks default 30-day retention. Confirm policy to ensure silver watermark covers full history on first load | Databricks admin | Confirm |
| 04 | Warehouse IDs for Claude attribution hardcoded in dashboard — if new Claude-queried warehouses are added, dashboard must be updated | Data + Automation | Monitor |
| 05 | Future gold views — `gold_claude_cost_daily` and `gold_claude_user_benchmarks` can be added without schema changes if other consumers need Claude cost data | Data + Automation | Future |

---

## Key EDA Findings

| Table | Rows sampled | Distinct IDs | Notable findings |
| --- | --- | --- | --- |
| `silver_cluster_current` | 1,000 | 492 | 484 deleted clusters |
| `silver_warehouse_current` | 30 | 18 | 13 deleted warehouses |
| `silver_job_current` | 1,000 | 489 | `creator_email` NULL for 941 rows — no reliable owner |
| `silver_pipeline_current` | 1,000 | 402 | 85% duplicate rate — highest of all tables |
| `silver_served_entity_current` | 5 | 5 | FOUNDATION_MODEL rows always `System-User` — UNRESOLVED at gold by design |
| `silver_usage_history` | 275,577 | 275,577 | 100% unique `record_identifier` — 0 duplicates confirmed |
| `silver_query_history` | 1,852,210 | 1,852,210 | All statuses retained — FINISHED 96.31%, FAILED 3.63%, CANCELED 0.05% |
| `gold_query_history` | 1,783,948 | 1,783,948 | FINISHED only — 0 duplicates, 104 distinct users, 36 distinct client apps |

---

## References

- [Databricks Billable Usage System Table](https://docs.databricks.com/aws/en/admin/system-tables/billing)
- [Databricks List Prices System Table](https://docs.databricks.com/aws/en/admin/system-tables/pricing)
- [Databricks Query History System Table](https://docs.databricks.com/aws/en/admin/system-tables/query-history)
- Databricks Job Standards — Process Standards
- Silver + Gold Modeling Reference — Process Standards
- Unity Catalog Policy and Naming Standards — Process Standards
- Claude Cost Analytics — Table Design and Load Pattern Proposal v10 FINAL
- Claude Databricks Cost Attribution — Methodology Approval Document v10 FINAL
