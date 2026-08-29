# DnA - Databricks Cost Analytics Dashboard — Reference Export

Exported dashboard definition (Lakeview JSON) converted to a readable reference. The original `.json` file can be re-imported into Databricks Lakeview dashboards to fully recreate this dashboard, including layout and filters.

**Tabs:** 6  |  **Underlying queries:** 57

## Dashboard Tabs

- **Cost Summary** — 16 widgets
- **SQL MCP Estimated Cost** — 13 widgets
- **Object Ownership** — 14 widgets
- **Tagging & Attribution** — 15 widgets
- **README** — 1 widgets
- **App Cost** — 7 widgets

## Tab Details

### Cost Summary

- **Widget `total_spend_usd_counter`** (counter) — dataset(s): `total_spend_usd`
- **Widget `filter_date_range`** (filter-date-range-picker) — dataset(s): `spend_by_workspace_draft, spend_by_product_draft, monthly_spend_summary_draft, unresolved_spend_pct, top_10_skus_by_spend, daily_spend_trend_draft, 85ca5872, total_spend_usd, last_30_days_spend, projected_annual_spend_draft, spend_change_30d, monthly_spend_by_product_draft, spend_by_object_type_draft`
- **Widget `filter_billing_product`** (filter-multi-select) — dataset(s): `spend_by_workspace_draft, spend_by_product_draft, billing_product_options, monthly_spend_summary_draft, unresolved_spend_pct, top_10_skus_by_spend, daily_spend_trend_draft, 85ca5872, total_spend_usd, last_30_days_spend, projected_annual_spend_draft, spend_change_30d, monthly_spend_by_product_draft, spend_by_object_type_draft`
- **Widget `filter_object_type`** (filter-multi-select) — dataset(s): `spend_by_workspace_draft, spend_by_product_draft, monthly_spend_summary_draft, unresolved_spend_pct, top_10_skus_by_spend, daily_spend_trend_draft, 85ca5872, object_type_options, total_spend_usd, last_30_days_spend, projected_annual_spend_draft, spend_change_30d, monthly_spend_by_product_draft, spend_by_object_type_draft`
- **Widget `spend_change_30d_counter`** (counter) — dataset(s): `spend_change_30d`
- **Widget `last_30d_spend_counter`** (counter) — dataset(s): `last_30_days_spend`
- **Widget `projected_annual_counter`** (counter) — dataset(s): `projected_annual_spend_draft`
- **Widget `unresolved_spend_counter`** (counter) — dataset(s): `unresolved_spend_pct`
- **Widget `daily_spend_trend_line`** (line) — dataset(s): `daily_spend_trend_draft`
- **Widget `spend_by_product_bar`** (bar) — dataset(s): `spend_by_product_draft`
- **Widget `spend_by_object_type_donut`** (bar) — dataset(s): `spend_by_object_type_draft`
- **Widget `monthly_spend_by_product_bar`** (bar) — dataset(s): `monthly_spend_by_product_draft`
- **Widget `monthly_spend_summary_table`** (table) — dataset(s): `monthly_spend_summary_draft`
- **Widget `spend_by_workspace_bar`** (bar) — dataset(s): `spend_by_workspace_draft`
- **Widget `top_10_skus_bar`** (bar) — dataset(s): `top_10_skus_by_spend`
> **Complete Databricks spending picture from day one. This tab shows how much we are spending, what products and resources are driving cost, whether spend is accelerating or slowing, and which resources need immediate action. Use this tab to understand the overall cost picture before diving into ownership and attribution details.**


### SQL MCP Estimated Cost

- **Widget `filter_date_range`** (filter-date-range-picker) — dataset(s): `claude_vs_warehouse_monthly, claude_user_detail, claude_top_10_expensive_days, claude_cost_by_user_top10, claude_daily_cost_trend, claude_query_volume_daily, claude_pct_share_by_warehouse, claude_cost_summary, claude_monthly_trend, claude_cost_by_warehouse`
- **Widget `filter_warehouse`** (filter-multi-select) — dataset(s): `claude_vs_warehouse_monthly, claude_user_detail, claude_top_10_expensive_days, claude_cost_by_user_top10, claude_daily_cost_trend, claude_warehouse_options, claude_query_volume_daily, claude_pct_share_by_warehouse, claude_cost_summary, claude_monthly_trend, claude_cost_by_warehouse, claude_projected_monthly_cost, claude_june_avg_daily_cost`
- **Widget `filter_user`** (filter-multi-select) — dataset(s): `claude_vs_warehouse_monthly, claude_user_detail, claude_user_options, claude_top_10_expensive_days, claude_cost_by_user_top10, claude_daily_cost_trend, claude_query_volume_daily, claude_pct_share_by_warehouse, claude_cost_summary, claude_monthly_trend, claude_cost_by_warehouse, claude_projected_monthly_cost, claude_june_avg_daily_cost`
- **Widget `total_claude_cost_counter`** (counter) — dataset(s): `claude_cost_summary`
- **Widget `claude_cost_this_month_counter`** (counter) — dataset(s): `claude_cost_summary`
- **Widget `cost_per_query_counter`** (counter) — dataset(s): `claude_cost_summary`
- **Widget `monthly_claude_cost_trend`** (line) — dataset(s): `claude_monthly_trend`
- **Widget `claude_vs_warehouse_line`** (line) — dataset(s): `claude_vs_warehouse_monthly`
- **Widget `claude_cost_by_warehouse_bar`** (bar) — dataset(s): `claude_cost_by_warehouse`
- **Widget `claude_cost_by_user_bar`** (bar) — dataset(s): `claude_cost_by_user_top10`
- **Widget `claude_user_detail_table`** (table) — dataset(s): `claude_user_detail`
- **Widget `daily_volume_top5_users`** (bar) — dataset(s): `claude_daily_volume_top5_users`
> **This tab shows estimated compute cost attributed to SQL MCP connector queries - who is using it, how much it costs per query, which warehouses are being queried, and whether costs are growing month over month. All figures are pro-rata estimates based on task time weighting - exact per-client billing is not available from Databricks system tables.**


### Object Ownership

- **Widget `filter_object_type`** (filter-multi-select) — dataset(s): `obj_spend_by_attribution, obj_top10_unresolved, obj_idle_by_type, object_type_options, obj_full_list, obj_ownership_kpis, obj_spend_by_type, obj_spend_by_owner_top10`
- **Widget `filter_owner`** (filter-multi-select) — dataset(s): `obj_spend_by_attribution, obj_top10_unresolved, obj_idle_by_type, obj_owner_options, obj_ownership_kpis, obj_full_list, obj_spend_by_type, obj_spend_by_owner_top10`
- **Widget `total_objects_counter`** (counter) — dataset(s): `obj_ownership_kpis`
- **Widget `unresolved_spend_counter`** (counter) — dataset(s): `obj_ownership_kpis`
- **Widget `idle_objects_counter`** (counter) — dataset(s): `obj_ownership_kpis`
- **Widget `idle_cost_counter`** (counter) — dataset(s): `obj_ownership_kpis`
- **Widget `attribution_donut`** (pie) — dataset(s): `obj_spend_by_attribution`
- **Widget `top_owners_bar`** (bar) — dataset(s): `obj_spend_by_owner_top10`
- **Widget `spend_by_type_bar`** (bar) — dataset(s): `obj_spend_by_type`
- **Widget `idle_by_type_bar`** (bar) — dataset(s): `obj_idle_by_type`
- **Widget `full_object_list_table`** (table) — dataset(s): `obj_full_list`
- **Widget `filter_object_status`** (filter-single-select) — dataset(s): `obj_spend_by_attribution, obj_top10_unresolved, obj_idle_by_type, obj_full_list, obj_ownership_kpis, obj_status_options, obj_spend_by_type, obj_spend_by_owner_top10`
- **Widget `top_unresolved_table`** (table) — dataset(s): `obj_top10_unresolved`
> **This tab answers who owns each Databricks resource, what it has cost, and how long it has been sitting unused. No owner means no accountability. Idle means wasted spend. Use this tab to act.**


### Tagging & Attribution

- **Widget `filter_date_range`** (filter-date-range-picker) — dataset(s): `tag_kpis, tag_spend_by_domain, purpose_tag_coverage_pct, domain_tag_coverage_pct, tag_coverage_monthly, tag_spend_by_purpose, tag_detail, tag_spend_by_team, tag_untagged_by_product`
- **Widget `filter_team`** (filter-multi-select) — dataset(s): `tag_kpis, tag_spend_by_domain, purpose_tag_coverage_pct, domain_tag_coverage_pct, tag_coverage_monthly, tag_spend_by_purpose, tag_detail, tag_spend_by_team, tag_team_options, tag_untagged_by_product`
- **Widget `filter_domain`** (filter-multi-select) — dataset(s): `tag_kpis, tag_spend_by_domain, purpose_tag_coverage_pct, tag_domain_options, domain_tag_coverage_pct, tag_coverage_monthly, tag_spend_by_purpose, tag_detail, tag_spend_by_team, tag_untagged_by_product`
- **Widget `filter_purpose`** (filter-multi-select) — dataset(s): `tag_kpis, tag_spend_by_domain, purpose_tag_coverage_pct, tag_spend_by_team, tag_coverage_monthly, domain_tag_coverage_pct, tag_spend_by_purpose, tag_detail, tag_purpose_options, tag_untagged_by_product`
- **Widget `tag_coverage_counter`** (counter) — dataset(s): `tag_kpis`
- **Widget `untagged_spend_counter`** (counter) — dataset(s): `tag_kpis`
- **Widget `tag_coverage_line`** (line) — dataset(s): `tag_coverage_monthly`
- **Widget `spend_by_team_bar`** (bar) — dataset(s): `tag_spend_by_team`
- **Widget `spend_by_domain_bar`** (bar) — dataset(s): `tag_spend_by_domain`
- **Widget `spend_by_purpose_bar`** (bar) — dataset(s): `tag_spend_by_purpose`
- **Widget `untagged_by_product_bar`** (bar) — dataset(s): `tag_untagged_by_product`
- **Widget `tag_detail_table`** (table) — dataset(s): `tag_detail`
- **Widget `domain_tag_coverage_counter`** (counter) — dataset(s): `domain_tag_coverage_pct`
- **Widget `purpose_tag_coverage_counter`** (counter) — dataset(s): `purpose_tag_coverage_pct`
> **Tagging is how we trace every Databricks dollar back to a team, domain, and business purpose. Without tags we cannot do chargebacks, budget accountability, or answer which part of the business is driving platform costs. This tab shows how well we are tagging today, where the gaps are, and exactly which spend cannot be attributed.**


### README

> ## DnA — Databricks Cost Analytics Dashboard
 
 ### What is this dashboard?
 
 This dashboard provides full visibility into the organization's Databricks platform spend, Claude AI query cost attribution, resource ownership, and tagging coverage. It is built and maintained by the Data + Automation team.
 
 ---
 
 ### Who is this for?
 
 * Leadership — platform cost visibility and governance
 * Data + Automation team — pipeline monitoring and attribution
 * Team leads — ownership accountability and resource management
 
 ---
 
 ### What questions does it answer?
 
 **Tab 1 — Cost Summary**
 
 * How much have we spent on Databricks total?
 * Is spend going up or down?
 * Which products and object types are driving cost?
 * Which resources are the most expensive?
 
 **Tab 2 — Claude Cost Attribution**
 
 * How much is Claude querying Databricks costing us?
 * Which users are driving Claude cost?
 * Which warehouses is Claude using?
 * Is Claude cost growing month over month?
 
 **Tab 3 — Object Ownership**
 
 * Which resources have no owner assigned?
 * Which resources are idle and burning money?
 * Who owns the most expensive resources?
 
 **Tab 4 — Tagging & Attribution**
 
 * What % of spend has team, domain, and purpose tags?
 * Which teams and domains are spending the most?
 * Which resources are missing tags?
 
 ---
 
 ### How to Use This Dashboard — Analytical Reasoning
 
 This section explains HOW the dashboard answers the business questions above — the reasoning behind metric choices, how to interpret visualizations together, and what actions to take based on what you see.
 
 #### Reading the Cost Summary Tab
 
 **Start at the top, then drill down.** The counters give you the headline numbers; the charts below explain WHY those numbers look the way they do.
 
 **Total Spend** (counter)
 * What it tells you: Cumulative platform cost since Aug 2023
 * Next step: Compare against budget — is this tracking where leadership expected?
 
 **Last 30 Days + 30-Day Change %** (counters)
 * What it tells you: Recent velocity — is spend accelerating or decelerating?
 * Next step: If change % is positive and above 10%, investigate which product drove it using the "Spend by Product" chart below
 
 **Projected Annual Spend** (counter)
 * What it tells you: Annualized run-rate based on trailing 30-day average daily cost
 * Next step: This is NOT a forecast — it assumes current patterns continue unchanged. Use for budget conversations, not precise planning.
 
 **Unresolved Spend %** (counter)
 * What it tells you: Portion of cost with no identifiable owner
 * Next step: If >20%, pivot to the Object Ownership tab to triage unassigned resources
 
 **Chart relationships:**
 * **Daily Spend Trend** shows raw volatility. The 7-day rolling average removes day-of-week noise; the 30-day average reveals the structural trend. When the 7-day line crosses above the 30-day line, spend is accelerating.
 * **Monthly Spend by Product** (stacked bar) answers "is growth concentrated in one product or broad-based?" If a single color dominates the delta between months, that product needs attention.
 * **Top 10 SKUs** identifies the exact billing line items driving cost — use this when "Spend by Product" shows a spike but you need the specific SKU for a Databricks support or procurement conversation.
 
 #### Reading the Claude Cost Tab
 
 **The core question: Is Claude usage cost-effective relative to the value it delivers?**
 
 **Monthly Cost Trend** (line chart)
 * What it tells you: Whether Claude cost is growing proportionally with adoption (more users) or disproportionately (same users, more expensive queries)
 * Next step: Cross-reference with the Active Users counter — cost growth with flat user count = efficiency problem
 
 **Claude % Share of Warehouse Compute** (line chart)
 * What it tells you: How much of the serverless SQL bill is Claude
 * Next step: If this exceeds 30%, consider whether Claude workloads should run on a dedicated warehouse to isolate cost
 
 **Daily Volume by Top 5 Users** (stacked bar)
 * What it tells you: Whether cost is driven by a few heavy users or broadly distributed
 * Next step: If one user dominates, it may indicate an automated loop or an opportunity for query optimization
 
 **Cost per Query** (counter)
 * What it tells you: Efficiency benchmark for Claude queries
 * Next step: If this rises without a corresponding increase in query complexity, investigate whether result caching is being bypassed
 
 **Decision framework:**
 * Claude % of warehouse > 25% → evaluate dedicated warehouse isolation
 * cost\_per\_query > $0.05 → review top user query patterns for optimization
 * One user > 40% of total Claude cost → check if automated (MCP loop) or manual usage
 
 #### Reading the Object Ownership Tab
 
 **Purpose: Ensure every dollar of spend has an accountable owner.**
 
 This tab defaults to "Current (Active)" objects because deleted resources no longer represent actionable cost. Switch to "Historical" to audit past waste.
 
 **"How Is Spend Attributed?" donut**
 * What it tells you: The ratio of ownership resolution methods
 * Next step: "No Owner Identified" (UNRESOLVED) is the action item. The goal is to shrink this slice over time.
 
 **Top 10 Resolved Owners** (bar chart)
 * What it tells you: WHO is responsible for the most spend
 * Next step: This is not punitive — it enables optimization conversations with the right people
 
 **Idle Objects by Type** (bar chart)
 * What it tells you: Resources with >90 days of inactivity that still accrue cost
 * Next step: These are immediate candidates for deletion or archival
 
 **Top Unresolved Objects** (table)
 * What it tells you: The prioritized action list of unowned resources
 * Next step: Work through top-to-bottom by spend to assign owners
 
 **Decision framework:**
 * Idle Objects counter > 10 → schedule a resource cleanup sprint
 * Unresolved Spend > $500 → escalate to team leads for manual ownership assignment
 * An owner appears in "Top Owners" AND has idle objects → flag for decommissioning conversation
 
 #### Reading the Tagging & Attribution Tab
 
 **Purpose: Measure and improve cost allocation completeness.**
 
 Tags enable chargeback and showback. Without tags, cost cannot be attributed to the team/domain/purpose that incurred it.
 
 **Coverage % counters** (Team, Domain, Purpose)
 * What they tell you: What fraction of total spend is tagged along each dimension. 100% = full attribution.
 * Next step: Below 80% means significant cost is invisible to the responsible party — investigate using the Tag Detail table filtered by UNTAGGED
 
 **Tag Coverage Over Time** (line chart)
 * What it tells you: Whether tagging discipline is improving or degrading
 * Next step: A declining line means new resources are being deployed without tags — this is a process issue
 
 **Spend by Team/Domain/Purpose** (bar charts)
 * What they tell you: Where tagged spend is going
 * Next step: Use for chargeback conversations or to identify which organizational units drive the most consumption
 
 **Untagged Spend by Product** (bar chart)
 * What it tells you: Which Databricks products have the worst tagging compliance
 * Next step: If "SQL Warehouse" dominates, serverless resources may be spinning up without tag propagation
 
 **Decision framework:**
 * Any coverage % below 80% → investigate which new resources lack tags
 * Coverage declining month-over-month → new resource provisioning is not enforcing tags
 * One team > 40% of total spend → opportunity for targeted optimization engagement with that team
 
 #### Why These Metrics?
 
 **30-day rolling window for spend change**
 * Smooths weekday/weekend variance while remaining responsive to trend shifts
 * Alternatives: 7-day (too noisy for exec reporting), 90-day (too slow to detect changes)
 
 **Projected Annual = daily avg × 365**
 * Simple, explainable, no ML dependency
 * Alternative: Time-series forecasting (adds complexity and maintenance burden for marginal accuracy gain)
 
 **Claude cost via task\_duration pro-rata**
 * Only reliable attribution metric available; correlates with actual compute consumed
 * Alternatives: Query count (ignores duration differences), DBU (not exposed per-client by Databricks)
 
 **Idle threshold = 90 days of no activity**
 * Balances false positives (seasonal batch jobs) vs. waste detection
 * Alternatives: 30 days (too aggressive for monthly jobs), 180 days (too lenient — misses waste)
 
 **Tag coverage = spend-weighted %**
 * Ensures high-cost untagged resources weigh more than trivial ones
 * Alternative: Object-count % (a $0.01 untagged resource would count the same as a $10K one)
 
 ---
 
 ### Data Architecture
 
 **Important:** This dashboard does NOT query system tables directly. It reads from the **gold layer** produced by the DnA pipeline.
 
 **Raw sources (upstream — ingested by pipeline):**
 
 * system.billing.usage — Databricks billing records
 * system.billing.list\_prices — SKU pricing
 * system.compute.clusters — cluster metadata
 * system.compute.warehouses — warehouse metadata
 * system.lakeflow.jobs — job metadata
 * system.lakeflow.pipelines — pipeline metadata
 * system.access.workspaces\_latest — workspace metadata
 * system.serving.served\_entities — model serving metadata
 * system.query.history — query execution history (Claude attribution)
 
 **Gold layer (queried by dashboard):**
 
 * `data_automation.databricks_analytics.gold_fact_usage` — hourly spend fact (workspace × object × SKU × hour)
 * `data_automation.databricks_analytics.gold_dim_object` — object dimension (type, name, owner, idle days)
 * `data_automation.databricks_analytics.gold_dim_sku` — SKU dimension (billing product, price)
 * `data_automation.databricks_analytics.gold_dim_workspace` — workspace dimension (name, URL, status)
 * `data_automation.databricks_analytics.gold_query_history` — query telemetry (duration, user, warehouse, client app)
 * `data_automation.databricks_analytics.gold_top_cost_objects_current` — pre-ranked object snapshot with ownership
 
 If you query `system.billing.usage` directly, results will differ from this dashboard due to transformations, deduplication, and enrichment applied in the pipeline.
 
 ---
 
 ### Filter Behavior
 
 * Filters are **page-scoped** — each tab has its own independent filters
 * Default state is "All" (no filter applied) unless noted otherwise
 * Multi-select filters with nothing selected = no filter (shows all data)
 * Date range defaults: Cost Summary and Tagging start at 2023-08-30; Claude Cost starts at 2026-02-11 (first Claude query)
 * Object Ownership uses a single-select status filter defaulting to "Current (Active)" to exclude deleted resources
 
 ---
 
 ### Refresh Cadence
 
 * Pipeline runs daily at **6:00 AM America/Detroit** (prod)
 * Gold layer tables are typically available by **6:30 AM ET**
 * Dashboard queries execute on-demand against the latest gold layer state
 * There is no caching — each page load runs live queries against the warehouse
 
 ---
 
 ### Pipeline
 
 * Repository: internal-pipelines-repo
 * Domain: data\_automation
 * Schema: databricks\_analytics
 * Schedule: Daily at 6:00 AM America/Detroit (prod)
 
 ---
 
 ### Claude Cost Attribution Methodology
 
 Claude queries are identified by `client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')`.
 
 Cost is attributed using a pro-rata formula at daily grain:
 
 ```
 Claude Cost = Total Warehouse Cost
               × (Claude Task Seconds ÷ Total Task Seconds)
 ```
 
 * Attribution metric: total\_task\_duration\_ms
 * SKU in scope: PREMIUM\_SERVERLESS\_SQL\_COMPUTE\_US\_EAST
 * Date range: February 11, 2026 onwards (first Claude query)
 * Validated total: $462.02 (Feb 11 – Jun 11, 2026)
 
 All cost figures are estimates. Databricks does not expose per-client billing natively.
 
 ---
 
 ### Object Ownership Methodology
 
 Ownership is resolved via `gold_top_cost_objects_current` using the following hierarchy:
 
 1. **executed\_by\_identity** — the user who most frequently runs the resource (from query history)
 2. **owner\_email** — the owner set in system metadata (cluster creator, job owner, etc.)
 3. **UNRESOLVED** — no owner could be determined by either method
 
 The `attribution_method` column indicates which source was used. Objects marked UNRESOLVED appear in the "Top Unresolved Objects" table for manual triage.
 
 ---
 
 ### Tag Definitions
 
 Tags are applied at the resource level and propagated to spend via `gold_fact_usage`:
 
 * **team** (`tag_team_text`) — the organizational team responsible for the resource (e.g., "Data + Automation", "Estimating")
 * **domain** (`tag_domain_text`) — the business domain the resource serves (e.g., "Finance", "Operations")
 * **purpose** (`tag_purpose_text`) — the functional purpose of the resource (e.g., "ETL", "Analytics", "ML Training")
 
 Resources without tags are marked `UNTAGGED`. Tag coverage % = (spend with tag ÷ total spend) × 100.
 
 ---
 
 ### Known Limitations
 
 * Claude application surface (web, Claude Code, API) cannot be distinguished — all use the same connector
 * FAILED queries excluded from cost attribution (0.01% of compute — negligible impact)
 * warehouse\_name is NULL for deleted warehouses
 * All timestamps are UTC
 
 ---
 
 ### Access & Permissions
 
 * **Viewers:** All organization Databricks workspace members can view the published dashboard
 * **Editors:** Data + Automation team members
 * **Data access:** Dashboard queries run with embedded credentials (viewer does not need direct table access)
 * **Request access:** Contact the Data + Automation team or submit via the #data-help channel
 
 ---
 
 ### Contacts
 
 * Dashboard owner: Data + Automation Team
 * Pipeline owner: Tushar
 * Reviewer: Data + Automation Team
 * For questions: Contact the Data + Automation team
 
 ---
 
 ### Version
 
 * Dashboard: v1.0 — June 2026
 * Pipeline: (internal tracking ticket)
 * Claude extension: DATA-TBD
 
 ---
 
 ### Change Log
 
 * **Jun 17, 2026** — Migrated all datasets from `dev_data_automation.databricks_analytics` to `data_automation.databricks_analytics` (production)
 * **Jun 12, 2026** — Added "How to Use This Dashboard" analytical reasoning section
 * **Jun 12, 2026** — Added Top 10 SKUs by Spend chart to Cost Summary
 * **Jun 12, 2026** — Added data labels to Claude Cost by User chart
 * **Jun 12, 2026** — Consolidated README into single comprehensive widget
 * **Jun 12, 2026** — Initial dashboard release (v1.0)


### App Cost

- **Widget `bd1e9b62`** (filter-date-range-picker) — dataset(s): `spend_by_workspace_draft, spend_by_product_draft, monthly_spend_summary_draft, unresolved_spend_pct, top_10_skus_by_spend, daily_spend_trend_draft, 85ca5872, total_spend_usd, last_30_days_spend, projected_annual_spend_draft, spend_change_30d, monthly_spend_by_product_draft, spend_by_object_type_draft`
- **Widget `dde02f92`** (filter-multi-select) — dataset(s): `spend_by_workspace_draft, spend_by_product_draft, billing_product_options, monthly_spend_summary_draft, unresolved_spend_pct, top_10_skus_by_spend, daily_spend_trend_draft, 85ca5872, total_spend_usd, last_30_days_spend, projected_annual_spend_draft, spend_change_30d, monthly_spend_by_product_draft, spend_by_object_type_draft`
- **Widget `6b5cf567`** (filter-multi-select) — dataset(s): `spend_by_workspace_draft, spend_by_product_draft, monthly_spend_summary_draft, unresolved_spend_pct, top_10_skus_by_spend, daily_spend_trend_draft, 85ca5872, object_type_options, total_spend_usd, last_30_days_spend, projected_annual_spend_draft, spend_change_30d, monthly_spend_by_product_draft, spend_by_object_type_draft`
> **Complete Databricks spending picture from day one. This tab shows how much we are spending, what products and resources are driving cost, whether spend is accelerating or slowing, and which resources need immediate action. Use this tab to understand the overall cost picture before diving into ownership and attribution details.**

- **Widget `76a8c52e`** (bar) — dataset(s): `e95af4d2`
- **Widget `1475b314`** (table) — dataset(s): `e95af4d2`
- **Widget `5134dd4c`** (line) — dataset(s): `125a56d0`

## SQL Query Reference

All underlying datasets, keyed by internal dataset name (referenced above).

### `85ca5872` — total_spend_all_time

```sql
SELECT
  CAST(SUM(f.total_cost) AS DECIMAL(18, 2)) AS total_spend_all_time
FROM
  data_automation.databricks_analytics.gold_fact_usage f
    JOIN data_automation.databricks_analytics.gold_dim_sku s
      ON f.sku_sk = s.sku_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_object o
      ON f.object_sk = o.object_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
      ON f.workspace_sk = w.workspace_sk
WHERE
  f.usage_date >= :date_range.min
  AND f.usage_date <= :date_range.max
  AND (
    SIZE(:billing_product) = 0
    OR array_contains(:billing_product, s.billing_origin_product)
  )
  AND (
    o.object_type IS NULL
    OR SIZE(:object_type) = 0
    OR array_contains(:object_type, o.object_type)
  )
  AND (
    w.workspace_name IS NULL
    OR SIZE(:workspace) = 0
    OR array_contains(:workspace, w.workspace_name)
  )
```

**Parameters:** `date_range` (Date Range), `billing_product` (Product), `object_type` (Object Type), `workspace` (Workspace)

### `total_spend_usd` — Total Spend USD

```sql
SELECT
  CAST(SUM(f.total_cost) AS DECIMAL(18, 2)) AS total_spend_usd
FROM
  data_automation.databricks_analytics.gold_fact_usage f
    JOIN data_automation.databricks_analytics.gold_dim_sku s
      ON f.sku_sk = s.sku_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_object o
      ON f.object_sk = o.object_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
      ON f.workspace_sk = w.workspace_sk
WHERE
  f.usage_date >= :date_range.min
  AND f.usage_date <= :date_range.max
  AND (
    SIZE(:billing_product) = 0
    OR array_contains(:billing_product, s.billing_origin_product)
  )
  AND (
    o.object_type IS NULL
    OR SIZE(:object_type) = 0
    OR array_contains(:object_type, o.object_type)
  )
  AND (
    w.workspace_name IS NULL
    OR SIZE(:workspace) = 0
    OR array_contains(:workspace, w.workspace_name)
  )
```

**Parameters:** `date_range` (Date Range), `billing_product` (Billing Product), `object_type` (Object Type), `workspace` (Workspace)

### `workspace_options` — workspace_options

```sql
SELECT DISTINCT
  workspace_name
FROM
  (
    SELECT
      workspace_name
    FROM
      data_automation.databricks_analytics.gold_dim_workspace
    WHERE
      workspace_name IS NOT NULL
    UNION ALL
    SELECT
      'Decommissioned' AS workspace_name
  ) t
ORDER BY
  workspace_name
```

### `object_type_options` — object_type_options

```sql
SELECT DISTINCT
  object_type
FROM
  data_automation.databricks_analytics.gold_dim_object
ORDER BY
  object_type
```

### `billing_product_options` — billing_product_options

```sql
SELECT DISTINCT
  billing_origin_product
FROM
  data_automation.databricks_analytics.gold_dim_sku
WHERE
  billing_origin_product IS NOT NULL
ORDER BY
  billing_origin_product
```

### `spend_change_30d` — spend_change_30d

```sql
SELECT
  CAST(
    SUM(
      CASE
        WHEN f.usage_date >= DATEADD(DAY, -30, CURRENT_DATE()) THEN f.total_cost
        ELSE 0
      END
    ) AS DECIMAL(18, 2)
  ) AS last_30_days,
  CAST(
    SUM(
      CASE
        WHEN
          f.usage_date >= DATEADD(DAY, -60, CURRENT_DATE())
          AND f.usage_date < DATEADD(DAY, -30, CURRENT_DATE())
        THEN
          f.total_cost
        ELSE 0
      END
    ) AS DECIMAL(18, 2)
  ) AS prior_30_days,
  ROUND(
    (
      SUM(
        CASE
          WHEN f.usage_date >= DATEADD(DAY, -30, CURRENT_DATE()) THEN f.total_cost
          ELSE 0
        END
      )
        - SUM(
          CASE
            WHEN
              f.usage_date >= DATEADD(DAY, -60, CURRENT_DATE())
              AND f.usage_date < DATEADD(DAY, -30, CURRENT_DATE())
            THEN
              f.total_cost
            ELSE 0
          END
        )
    )
      * 100.0
      / NULLIF(
        SUM(
          CASE
            WHEN
              f.usage_date >= DATEADD(DAY, -60, CURRENT_DATE())
              AND f.usage_date < DATEADD(DAY, -30, CURRENT_DATE())
            THEN
              f.total_cost
            ELSE 0
          END
        ),
        0
      ),
    2
  ) AS pct_change
FROM
  data_automation.databricks_analytics.gold_fact_usage f
    JOIN data_automation.databricks_analytics.gold_dim_sku s
      ON f.sku_sk = s.sku_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_object o
      ON f.object_sk = o.object_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
      ON f.workspace_sk = w.workspace_sk
WHERE
  f.usage_date >= :date_range.min
  AND f.usage_date <= :date_range.max
  AND (
    SIZE(:billing_product) = 0
    OR array_contains(:billing_product, s.billing_origin_product)
  )
  AND (
    o.object_type IS NULL
    OR SIZE(:object_type) = 0
    OR array_contains(:object_type, o.object_type)
  )
  AND (
    w.workspace_name IS NULL
    OR SIZE(:workspace) = 0
    OR array_contains(:workspace, w.workspace_name)
  )
```

**Parameters:** `date_range` (Date Range), `billing_product` (Product), `object_type` (Object Type), `workspace` (Workspace)

### `last_30_days_spend` — last_30_days_spend

```sql
SELECT
  CAST(SUM(f.total_cost) AS DECIMAL(18, 2)) AS last_30_days_spend
FROM
  data_automation.databricks_analytics.gold_fact_usage f
    JOIN data_automation.databricks_analytics.gold_dim_sku s
      ON f.sku_sk = s.sku_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_object o
      ON f.object_sk = o.object_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
      ON f.workspace_sk = w.workspace_sk
WHERE
  f.usage_date >= DATEADD(DAY, -30, CURRENT_DATE())
  AND f.usage_date >= :date_range.min
  AND f.usage_date <= :date_range.max
  AND (
    SIZE(:billing_product) = 0
    OR array_contains(:billing_product, s.billing_origin_product)
  )
  AND (
    o.object_type IS NULL
    OR SIZE(:object_type) = 0
    OR array_contains(:object_type, o.object_type)
  )
  AND (
    w.workspace_name IS NULL
    OR SIZE(:workspace) = 0
    OR array_contains(:workspace, w.workspace_name)
  )
```

**Parameters:** `date_range` (Date Range), `billing_product` (Product), `object_type` (Object Type), `workspace` (Workspace)

### `projected_annual_spend_draft` — projected_annual_spend_draft

```sql
SELECT
  CAST(
    SUM(f.total_cost) / COUNT(DISTINCT f.usage_date) * 365 AS DECIMAL(18, 2)
  ) AS projected_annual_spend
FROM
  data_automation.databricks_analytics.gold_fact_usage f
    JOIN data_automation.databricks_analytics.gold_dim_sku s
      ON f.sku_sk = s.sku_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_object o
      ON f.object_sk = o.object_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
      ON f.workspace_sk = w.workspace_sk
WHERE
  f.usage_date >= DATEADD(DAY, -30, CURRENT_DATE())
  AND f.usage_date >= :date_range.min
  AND f.usage_date <= :date_range.max
  AND (
    SIZE(:billing_product) = 0
    OR array_contains(:billing_product, s.billing_origin_product)
  )
  AND (
    o.object_type IS NULL
    OR SIZE(:object_type) = 0
    OR array_contains(:object_type, o.object_type)
  )
  AND (
    w.workspace_name IS NULL
    OR SIZE(:workspace) = 0
    OR array_contains(:workspace, w.workspace_name)
  )
```

**Parameters:** `date_range` (Date Range), `billing_product` (Product), `object_type` (Object Type), `workspace` (Workspace)

### `unresolved_spend_pct` — unresolved_spend_pct

```sql
SELECT
  ROUND(
    SUM(
      CASE
        WHEN o.owner_identity IS NULL THEN f.total_cost
        ELSE 0
      END
    )
      * 100.0
      / NULLIF(SUM(f.total_cost), 0),
    2
  ) AS unresolved_spend_pct
FROM
  data_automation.databricks_analytics.gold_fact_usage f
    LEFT JOIN data_automation.databricks_analytics.gold_dim_object o
      ON f.object_sk = o.object_sk
    JOIN data_automation.databricks_analytics.gold_dim_sku s
      ON f.sku_sk = s.sku_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
      ON f.workspace_sk = w.workspace_sk
WHERE
  f.usage_date >= :date_range.min
  AND f.usage_date <= :date_range.max
  AND (
    SIZE(:billing_product) = 0
    OR array_contains(:billing_product, s.billing_origin_product)
  )
  AND (
    o.object_type IS NULL
    OR SIZE(:object_type) = 0
    OR array_contains(:object_type, o.object_type)
  )
  AND (
    w.workspace_name IS NULL
    OR SIZE(:workspace) = 0
    OR array_contains(:workspace, w.workspace_name)
  )
```

**Parameters:** `date_range` (Date Range), `billing_product` (Product), `object_type` (Object Type), `workspace` (Workspace)

### `daily_spend_trend_draft` — daily_spend_trend_draft

```sql
WITH daily AS (
  SELECT
    f.usage_date,
    CAST(SUM(f.total_cost) AS DECIMAL(18, 2)) AS daily_spend
  FROM
    data_automation.databricks_analytics.gold_fact_usage f
      JOIN data_automation.databricks_analytics.gold_dim_sku s
        ON f.sku_sk = s.sku_sk
      LEFT JOIN data_automation.databricks_analytics.gold_dim_object o
        ON f.object_sk = o.object_sk
      LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
        ON f.workspace_sk = w.workspace_sk
  WHERE
    f.usage_date >= :date_range.min
    AND f.usage_date <= :date_range.max
    AND (
      SIZE(:billing_product) = 0
      OR array_contains(:billing_product, s.billing_origin_product)
    )
    AND (
      o.object_type IS NULL
      OR SIZE(:object_type) = 0
      OR array_contains(:object_type, o.object_type)
    )
    AND (
      w.workspace_name IS NULL
      OR SIZE(:workspace) = 0
      OR array_contains(:workspace, w.workspace_name)
    )
  GROUP BY
    f.usage_date
)
SELECT
  usage_date,
  daily_spend,
  CAST(
    AVG(daily_spend) OVER (
        ORDER BY usage_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
      ) AS DECIMAL(18, 2)
  ) AS rolling_7_day_avg,
  CAST(
    AVG(daily_spend) OVER (
        ORDER BY usage_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
      ) AS DECIMAL(18, 2)
  ) AS rolling_30_day_avg
FROM
  daily
ORDER BY
  usage_date
```

**Parameters:** `date_range` (Date Range), `billing_product` (Product), `object_type` (Object Type), `workspace` (Workspace)

### `spend_by_product_draft` — spend_by_product_draft

```sql
SELECT
  sk.billing_origin_product AS product,
  CAST(SUM(f.total_cost) AS DECIMAL(18, 2)) AS total_spend,
  ROUND(SUM(f.total_cost) * 100.0 / SUM(SUM(f.total_cost)) OVER (), 2) AS pct_of_total
FROM
  data_automation.databricks_analytics.gold_fact_usage f
    JOIN data_automation.databricks_analytics.gold_dim_sku sk
      ON f.sku_sk = sk.sku_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_object o
      ON f.object_sk = o.object_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
      ON f.workspace_sk = w.workspace_sk
WHERE
  f.usage_date >= :date_range.min
  AND f.usage_date <= :date_range.max
  AND (
    SIZE(:billing_product) = 0
    OR array_contains(:billing_product, sk.billing_origin_product)
  )
  AND (
    o.object_type IS NULL
    OR SIZE(:object_type) = 0
    OR array_contains(:object_type, o.object_type)
  )
  AND (
    w.workspace_name IS NULL
    OR SIZE(:workspace) = 0
    OR array_contains(:workspace, w.workspace_name)
  )
GROUP BY
  sk.billing_origin_product
ORDER BY
  total_spend DESC
```

**Parameters:** `date_range` (Date Range), `billing_product` (Product), `object_type` (Object Type), `workspace` (Workspace)

### `spend_by_object_type_draft` — spend_by_object_type_draft

```sql
SELECT
  o.object_type,
  CAST(SUM(f.total_cost) AS DECIMAL(18, 2)) AS total_spend,
  ROUND(SUM(f.total_cost) * 100.0 / SUM(SUM(f.total_cost)) OVER (), 2) AS pct_of_total
FROM
  data_automation.databricks_analytics.gold_fact_usage f
    JOIN data_automation.databricks_analytics.gold_dim_object o
      ON f.object_sk = o.object_sk
    JOIN data_automation.databricks_analytics.gold_dim_sku sk
      ON f.sku_sk = sk.sku_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
      ON f.workspace_sk = w.workspace_sk
WHERE
  f.usage_date >= :date_range.min
  AND f.usage_date <= :date_range.max
  AND (
    SIZE(:billing_product) = 0
    OR array_contains(:billing_product, sk.billing_origin_product)
  )
  AND (
    o.object_type IS NULL
    OR SIZE(:object_type) = 0
    OR array_contains(:object_type, o.object_type)
  )
  AND (
    w.workspace_name IS NULL
    OR SIZE(:workspace) = 0
    OR array_contains(:workspace, w.workspace_name)
  )
GROUP BY
  o.object_type
ORDER BY
  total_spend DESC
```

**Parameters:** `date_range` (Date Range), `billing_product` (Product), `object_type` (Object Type), `workspace` (Workspace)

### `monthly_spend_by_product_draft` — monthly_spend_by_product_draft

```sql
SELECT
  DATE_TRUNC('MONTH', f.usage_date) AS month,
  sk.billing_origin_product AS product,
  CAST(SUM(f.total_cost) AS DECIMAL(18, 2)) AS total_spend
FROM
  data_automation.databricks_analytics.gold_fact_usage f
    JOIN data_automation.databricks_analytics.gold_dim_sku sk
      ON f.sku_sk = sk.sku_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_object o
      ON f.object_sk = o.object_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
      ON f.workspace_sk = w.workspace_sk
WHERE
  f.usage_date >= :date_range.min
  AND f.usage_date <= :date_range.max
  AND (
    SIZE(:billing_product) = 0
    OR array_contains(:billing_product, sk.billing_origin_product)
  )
  AND (
    o.object_type IS NULL
    OR SIZE(:object_type) = 0
    OR array_contains(:object_type, o.object_type)
  )
  AND (
    w.workspace_name IS NULL
    OR SIZE(:workspace) = 0
    OR array_contains(:workspace, w.workspace_name)
  )
GROUP BY
  DATE_TRUNC('MONTH', f.usage_date),
  sk.billing_origin_product
ORDER BY
  month,
  total_spend DESC
```

**Parameters:** `date_range` (Date Range), `billing_product` (Product), `object_type` (Object Type), `workspace` (Workspace)

### `monthly_spend_summary_draft` — monthly_spend_summary_draft

```sql
WITH daily AS (
  SELECT
    f.usage_date,
    CAST(SUM(f.total_cost) AS DECIMAL(18, 2)) AS daily_cost
  FROM
    data_automation.databricks_analytics.gold_fact_usage f
      JOIN data_automation.databricks_analytics.gold_dim_sku s
        ON f.sku_sk = s.sku_sk
      LEFT JOIN data_automation.databricks_analytics.gold_dim_object o
        ON f.object_sk = o.object_sk
      LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
        ON f.workspace_sk = w.workspace_sk
  WHERE
    f.usage_date >= :date_range.min
    AND f.usage_date <= :date_range.max
    AND (
      SIZE(:billing_product) = 0
      OR array_contains(:billing_product, s.billing_origin_product)
    )
    AND (
      o.object_type IS NULL
      OR SIZE(:object_type) = 0
      OR array_contains(:object_type, o.object_type)
    )
    AND (
      w.workspace_name IS NULL
      OR SIZE(:workspace) = 0
      OR array_contains(:workspace, w.workspace_name)
    )
  GROUP BY
    f.usage_date
),
monthly AS (
  SELECT
    DATE_TRUNC('MONTH', usage_date) AS month_sort,
    CAST(SUM(daily_cost) AS DECIMAL(18, 2)) AS monthly_spend,
    ROUND(AVG(daily_cost), 2) AS avg_daily_spend,
    CAST(MIN(daily_cost) AS DECIMAL(18, 2)) AS min_daily_spend,
    CAST(MAX(daily_cost) AS DECIMAL(18, 2)) AS max_daily_spend,
    COUNT(DISTINCT usage_date) AS days_billed
  FROM
    daily
  GROUP BY
    DATE_TRUNC('MONTH', usage_date)
)
SELECT
  DATE_FORMAT(month_sort, 'MMM yyyy') AS month,
  month_sort,
  monthly_spend,
  avg_daily_spend,
  min_daily_spend,
  max_daily_spend,
  days_billed,
  CAST(
    SUM(monthly_spend) OVER (
        ORDER BY month_sort
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
      ) AS DECIMAL(18, 2)
  ) AS running_total
FROM
  monthly
ORDER BY
  month_sort DESC
```

**Parameters:** `date_range` (Date Range), `billing_product` (Product), `object_type` (Object Type), `workspace` (Workspace)

### `spend_by_workspace_draft` — spend_by_workspace_draft

```sql
SELECT
  COALESCE(w.workspace_name, 'Decommissioned') AS workspace_name,
  CAST(SUM(f.total_cost) AS DECIMAL(18, 2)) AS total_spend,
  ROUND(SUM(f.total_cost) * 100.0 / SUM(SUM(f.total_cost)) OVER (), 2) AS pct_of_total
FROM
  data_automation.databricks_analytics.gold_fact_usage f
    JOIN data_automation.databricks_analytics.gold_dim_sku s
      ON f.sku_sk = s.sku_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_object o
      ON f.object_sk = o.object_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
      ON f.workspace_sk = w.workspace_sk
WHERE
  f.usage_date >= :date_range.min
  AND f.usage_date <= :date_range.max
  AND (
    SIZE(:billing_product) = 0
    OR array_contains(:billing_product, s.billing_origin_product)
  )
  AND (
    o.object_type IS NULL
    OR SIZE(:object_type) = 0
    OR array_contains(:object_type, o.object_type)
  )
  AND (
    w.workspace_name IS NULL
    OR SIZE(:workspace) = 0
    OR array_contains(:workspace, w.workspace_name)
  )
GROUP BY
  COALESCE(w.workspace_name, 'Decommissioned')
ORDER BY
  total_spend DESC
```

**Parameters:** `date_range` (Date Range), `billing_product` (Product), `object_type` (Object Type), `workspace` (Workspace)

### `top_10_skus_by_spend` — top_10_skus_by_spend

```sql
SELECT
  sk.sku_name,
  sk.billing_origin_product AS product,
  CAST(SUM(f.total_cost) AS DECIMAL(18, 2)) AS total_spend,
  ROUND(SUM(f.total_cost) * 100.0 / SUM(SUM(f.total_cost)) OVER (), 2) AS pct_of_total
FROM
  data_automation.databricks_analytics.gold_fact_usage f
    JOIN data_automation.databricks_analytics.gold_dim_sku sk
      ON f.sku_sk = sk.sku_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_object o
      ON f.object_sk = o.object_sk
    LEFT JOIN data_automation.databricks_analytics.gold_dim_workspace w
      ON f.workspace_sk = w.workspace_sk
WHERE
  f.usage_date >= :date_range.min
  AND f.usage_date <= :date_range.max
  AND (
    SIZE(:billing_product) = 0
    OR array_contains(:billing_product, sk.billing_origin_product)
  )
  AND (
    o.object_type IS NULL
    OR SIZE(:object_type) = 0
    OR array_contains(:object_type, o.object_type)
  )
  AND (
    w.workspace_name IS NULL
    OR SIZE(:workspace) = 0
    OR array_contains(:workspace, w.workspace_name)
  )
GROUP BY
  sk.sku_name,
  sk.billing_origin_product
ORDER BY
  total_spend DESC
LIMIT 10
```

**Parameters:** `date_range` (Date Range), `billing_product` (Product), `object_type` (Object Type), `workspace` (Workspace)

### `top_cost_objects` — top_cost_objects

```sql
SELECT
  cost_rank AS rank,
  object_type,
  COALESCE(object_name, object_identifier) AS object_name,
  COALESCE(owner_identity, 'UNRESOLVED') AS owner,
  CAST(total_cost AS DECIMAL(18, 2)) AS total_spend,
  last_activity_date,
  idle_day_count
FROM
  data_automation.databricks_analytics.gold_top_cost_objects_current
WHERE
  cost_rank <= 10
ORDER BY
  cost_rank
```

### `claude_warehouse_options` — sql_mcp_warehouse_options

```sql
SELECT DISTINCT
  warehouse_name
FROM
  data_automation.databricks_analytics.gold_query_history
WHERE
  warehouse_name IS NOT NULL
ORDER BY
  warehouse_name
```

### `claude_user_options` — sql_mcp_user_options

```sql
SELECT DISTINCT
  executed_by_identity
FROM
  data_automation.databricks_analytics.gold_query_history
WHERE
  client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
  AND executed_by_identity IS NOT NULL
ORDER BY
  executed_by_identity
```

### `claude_cost_summary` — sql_mcp_cost_summary

```sql
WITH warehouse_cost AS (
  SELECT
    o.object_identifier AS warehouse_identifier,
    f.usage_date,
    SUM(f.total_cost) AS total_warehouse_cost_usd
  FROM
    data_automation.databricks_analytics.gold_fact_usage f
      JOIN data_automation.databricks_analytics.gold_dim_object o
        ON f.object_sk = o.object_sk
        AND o.object_type = 'WAREHOUSE'
      JOIN data_automation.databricks_analytics.gold_dim_sku s
        ON f.sku_sk = s.sku_sk
        AND s.sku_name = 'PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST'
  WHERE
    f.usage_date >= :date_range.min
    AND f.usage_date <= :date_range.max
  GROUP BY
    o.object_identifier,
    f.usage_date
),
claude_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS claude_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
    AND (
      SIZE(:user) = 0
      OR array_contains(:user, executed_by_identity)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
total_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS total_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
daily_attributed AS (
  SELECT
    ct.usage_date,
    ROUND(
      wc.total_warehouse_cost_usd * ct.claude_task_seconds / NULLIF(tt.total_task_seconds, 0),
      4
    ) AS claude_cost
  FROM
    claude_task ct
      JOIN total_task tt
        ON ct.warehouse_identifier = tt.warehouse_identifier
        AND ct.usage_date = tt.usage_date
      JOIN warehouse_cost wc
        ON ct.warehouse_identifier = wc.warehouse_identifier
        AND ct.usage_date = wc.usage_date
),
query_stats AS (
  SELECT
    COUNT(*) AS total_queries,
    COUNT(DISTINCT executed_by_identity) AS active_users
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
    AND (
      SIZE(:user) = 0
      OR array_contains(:user, executed_by_identity)
    )
)
SELECT
  CAST(SUM(claude_cost) AS DECIMAL(18, 2)) AS total_claude_cost,
  CAST(
    SUM(
      CASE
        WHEN usage_date >= DATE_TRUNC('MONTH', CURRENT_DATE()) THEN claude_cost
        ELSE 0
      END
    ) AS DECIMAL(18, 2)
  ) AS cost_this_month,
  CAST(
    ROUND(
      SUM(claude_cost)
        / NULLIF(
          (
            SELECT
              total_queries
            FROM
              query_stats
          ),
          0
        ),
      4
    ) AS DECIMAL(18, 4)
  ) AS cost_per_query,
  (
    SELECT
      active_users
    FROM
      query_stats
  ) AS active_users,
  (
    SELECT
      total_queries
    FROM
      query_stats
  ) AS total_queries
FROM
  daily_attributed
```

**Parameters:** `date_range` (Date Range), `warehouse` (Warehouse), `user` (User)

### `claude_monthly_trend` — sql_mcp_monthly_trend

```sql
WITH warehouse_cost AS (
  SELECT
    o.object_identifier AS warehouse_identifier,
    f.usage_date,
    SUM(f.total_cost) AS total_warehouse_cost_usd
  FROM
    data_automation.databricks_analytics.gold_fact_usage f
      JOIN data_automation.databricks_analytics.gold_dim_object o
        ON f.object_sk = o.object_sk
        AND o.object_type = 'WAREHOUSE'
      JOIN data_automation.databricks_analytics.gold_dim_sku s
        ON f.sku_sk = s.sku_sk
        AND s.sku_name = 'PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST'
  WHERE
    f.usage_date >= :date_range.min
    AND f.usage_date <= :date_range.max
  GROUP BY
    o.object_identifier,
    f.usage_date
),
claude_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS claude_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
    AND (
      SIZE(:user) = 0
      OR array_contains(:user, executed_by_identity)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
total_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS total_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
daily_attributed AS (
  SELECT
    ct.usage_date,
    SUM(
      wc.total_warehouse_cost_usd * ct.claude_task_seconds / NULLIF(tt.total_task_seconds, 0)
    ) AS claude_cost
  FROM
    claude_task ct
      JOIN total_task tt
        ON ct.warehouse_identifier = tt.warehouse_identifier
        AND ct.usage_date = tt.usage_date
      JOIN warehouse_cost wc
        ON ct.warehouse_identifier = wc.warehouse_identifier
        AND ct.usage_date = wc.usage_date
  GROUP BY
    ct.usage_date
)
SELECT
  DATE_TRUNC('MONTH', usage_date) AS month,
  CAST(SUM(claude_cost) AS DECIMAL(18, 2)) AS sql_mcp_estimated_cost,
  COUNT(DISTINCT usage_date) AS days_with_queries,
  ROUND(AVG(claude_cost), 2) AS avg_daily_cost
FROM
  daily_attributed
GROUP BY
  DATE_TRUNC('MONTH', usage_date)
ORDER BY
  month
```

**Parameters:** `date_range` (Date Range), `warehouse` (Warehouse), `user` (User)

### `claude_vs_warehouse_monthly` — sql_mcp_vs_warehouse_monthly

```sql
WITH warehouse_cost AS (
  SELECT
    o.object_identifier AS warehouse_identifier,
    f.usage_date,
    SUM(f.total_cost) AS total_warehouse_cost_usd
  FROM
    data_automation.databricks_analytics.gold_fact_usage f
      JOIN data_automation.databricks_analytics.gold_dim_object o
        ON f.object_sk = o.object_sk
        AND o.object_type = 'WAREHOUSE'
      JOIN data_automation.databricks_analytics.gold_dim_sku s
        ON f.sku_sk = s.sku_sk
        AND s.sku_name = 'PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST'
  WHERE
    f.usage_date >= :date_range.min
    AND f.usage_date <= :date_range.max
  GROUP BY
    o.object_identifier,
    f.usage_date
),
claude_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS claude_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
    AND (
      SIZE(:user) = 0
      OR array_contains(:user, executed_by_identity)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
total_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS total_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
daily_attributed AS (
  SELECT
    ct.usage_date,
    SUM(wc.total_warehouse_cost_usd) AS warehouse_cost,
    SUM(
      wc.total_warehouse_cost_usd * ct.claude_task_seconds / NULLIF(tt.total_task_seconds, 0)
    ) AS claude_cost
  FROM
    claude_task ct
      JOIN total_task tt
        ON ct.warehouse_identifier = tt.warehouse_identifier
        AND ct.usage_date = tt.usage_date
      JOIN warehouse_cost wc
        ON ct.warehouse_identifier = wc.warehouse_identifier
        AND ct.usage_date = wc.usage_date
  GROUP BY
    ct.usage_date
)
SELECT
  DATE_TRUNC('MONTH', usage_date) AS month,
  ROUND(SUM(claude_cost) * 100.0 / NULLIF(SUM(warehouse_cost), 0), 2) AS sql_mcp_pct_of_warehouse
FROM
  daily_attributed
GROUP BY
  DATE_TRUNC('MONTH', usage_date)
ORDER BY
  month
```

**Parameters:** `date_range` (Date Range), `warehouse` (Warehouse), `user` (User)

### `claude_cost_by_warehouse` — SQL MCP Cost by Warehouse

```sql
WITH warehouse_cost AS (
  SELECT
    o.object_identifier AS warehouse_identifier,
    f.usage_date,
    SUM(f.total_cost) AS total_warehouse_cost_usd
  FROM
    data_automation.databricks_analytics.gold_fact_usage f
      JOIN data_automation.databricks_analytics.gold_dim_object o
        ON f.object_sk = o.object_sk
        AND o.object_type = 'WAREHOUSE'
      JOIN data_automation.databricks_analytics.gold_dim_sku s
        ON f.sku_sk = s.sku_sk
        AND s.sku_name = 'PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST'
  WHERE
    f.usage_date >= :date_range.min
    AND f.usage_date <= :date_range.max
  GROUP BY
    o.object_identifier,
    f.usage_date
),
claude_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS claude_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
    AND (
      SIZE(:user) = 0
      OR array_contains(:user, executed_by_identity)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
total_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS total_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
)
SELECT
  COALESCE(q.warehouse_name, ct.warehouse_identifier) AS warehouse,
  CAST(
    SUM(
      wc.total_warehouse_cost_usd * ct.claude_task_seconds / NULLIF(tt.total_task_seconds, 0)
    ) AS DECIMAL(18, 2)
  ) AS sql_mcp_cost_usd
FROM
  claude_task ct
    JOIN total_task tt
      ON ct.warehouse_identifier = tt.warehouse_identifier
      AND ct.usage_date = tt.usage_date
    JOIN warehouse_cost wc
      ON ct.warehouse_identifier = wc.warehouse_identifier
      AND ct.usage_date = wc.usage_date
    LEFT JOIN (
      SELECT DISTINCT
        warehouse_identifier,
        warehouse_name
      FROM
        data_automation.databricks_analytics.gold_query_history
      WHERE
        warehouse_name IS NOT NULL
    ) q
      ON ct.warehouse_identifier = q.warehouse_identifier
GROUP BY
  COALESCE(q.warehouse_name, ct.warehouse_identifier)
ORDER BY
  sql_mcp_cost_usd DESC
```

**Parameters:** `date_range` (Date Range), `warehouse` (Warehouse), `user` (User)

### `claude_query_volume_daily` — sql_mcp_query_volume_daily

```sql
SELECT
  query_start_date AS date,
  COUNT(*) AS total_queries,
  COUNT(
    CASE
      WHEN result_cache_hit_indicator = TRUE THEN 1
    END
  ) AS cache_hits,
  COUNT(
    CASE
      WHEN
        result_cache_hit_indicator = FALSE
        OR result_cache_hit_indicator IS NULL
      THEN
        1
    END
  ) AS fresh_computes
FROM
  data_automation.databricks_analytics.gold_query_history
WHERE
  client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
  AND query_start_date >= :date_range.min
  AND query_start_date <= :date_range.max
  AND (
    SIZE(:warehouse) = 0
    OR array_contains(:warehouse, warehouse_name)
  )
  AND (
    SIZE(:user) = 0
    OR array_contains(:user, executed_by_identity)
  )
GROUP BY
  query_start_date
ORDER BY
  date
```

**Parameters:** `date_range` (Date Range), `warehouse` (Warehouse), `user` (User)

### `claude_cost_by_user_top10` — sql_mcp_cost_by_user_top10

```sql
WITH warehouse_cost AS (
  SELECT
    o.object_identifier AS warehouse_identifier,
    f.usage_date,
    SUM(f.total_cost) AS total_warehouse_cost_usd
  FROM
    data_automation.databricks_analytics.gold_fact_usage f
      JOIN data_automation.databricks_analytics.gold_dim_object o
        ON f.object_sk = o.object_sk
        AND o.object_type = 'WAREHOUSE'
      JOIN data_automation.databricks_analytics.gold_dim_sku s
        ON f.sku_sk = s.sku_sk
        AND s.sku_name = 'PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST'
  WHERE
    f.usage_date >= :date_range.min
    AND f.usage_date <= :date_range.max
  GROUP BY
    o.object_identifier,
    f.usage_date
),
user_task AS (
  SELECT
    executed_by_identity,
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS user_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
    AND (
      SIZE(:user) = 0
      OR array_contains(:user, executed_by_identity)
    )
  GROUP BY
    executed_by_identity,
    warehouse_identifier,
    query_start_date
),
total_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS total_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
claude_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS claude_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
)
SELECT
  ut.executed_by_identity AS user,
  CAST(
    SUM(
      wc.total_warehouse_cost_usd
        * (ut.user_task_seconds / NULLIF(ct.claude_task_seconds, 0))
        * (ct.claude_task_seconds / NULLIF(tt.total_task_seconds, 0))
    ) AS DECIMAL(18, 2)
  ) AS estimated_user_cost
FROM
  user_task ut
    JOIN total_task tt
      ON ut.warehouse_identifier = tt.warehouse_identifier
      AND ut.usage_date = tt.usage_date
    JOIN claude_task ct
      ON ut.warehouse_identifier = ct.warehouse_identifier
      AND ut.usage_date = ct.usage_date
    JOIN warehouse_cost wc
      ON ut.warehouse_identifier = wc.warehouse_identifier
      AND ut.usage_date = wc.usage_date
GROUP BY
  ut.executed_by_identity
ORDER BY
  estimated_user_cost DESC
LIMIT 10
```

**Parameters:** `date_range` (Date Range), `warehouse` (Warehouse), `user` (User)

### `claude_user_detail` — sql_mcp_user_detail

```sql
WITH warehouse_cost AS (
  SELECT
    o.object_identifier AS warehouse_identifier,
    f.usage_date,
    SUM(f.total_cost) AS total_warehouse_cost_usd
  FROM
    data_automation.databricks_analytics.gold_fact_usage f
      JOIN data_automation.databricks_analytics.gold_dim_object o
        ON f.object_sk = o.object_sk
        AND o.object_type = 'WAREHOUSE'
      JOIN data_automation.databricks_analytics.gold_dim_sku s
        ON f.sku_sk = s.sku_sk
        AND s.sku_name = 'PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST'
  WHERE
    f.usage_date >= :date_range.min
    AND f.usage_date <= :date_range.max
  GROUP BY
    o.object_identifier,
    f.usage_date
),
user_task AS (
  SELECT
    executed_by_identity,
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS user_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
    AND (
      SIZE(:user) = 0
      OR array_contains(:user, executed_by_identity)
    )
  GROUP BY
    executed_by_identity,
    warehouse_identifier,
    query_start_date
),
total_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS total_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
claude_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS claude_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
query_stats AS (
  SELECT
    executed_by_identity,
    COUNT(*) AS total_queries,
    COUNT(DISTINCT query_start_date) AS active_days,
    MIN(query_start_date) AS first_query_date,
    MAX(query_start_date) AS last_query_date,
    COUNT(
      CASE
        WHEN result_cache_hit_indicator = TRUE THEN 1
      END
    ) AS cache_hits
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
    AND (
      SIZE(:user) = 0
      OR array_contains(:user, executed_by_identity)
    )
  GROUP BY
    executed_by_identity
)
SELECT
  ut.executed_by_identity AS user,
  qs.total_queries,
  CAST(
    SUM(
      wc.total_warehouse_cost_usd
        * (ut.user_task_seconds / NULLIF(ct.claude_task_seconds, 0))
        * (ct.claude_task_seconds / NULLIF(tt.total_task_seconds, 0))
    ) AS DECIMAL(18, 2)
  ) AS estimated_cost_usd,
  ROUND(
    SUM(
      wc.total_warehouse_cost_usd
        * (ut.user_task_seconds / NULLIF(ct.claude_task_seconds, 0))
        * (ct.claude_task_seconds / NULLIF(tt.total_task_seconds, 0))
    )
      / NULLIF(qs.total_queries, 0),
    4
  ) AS cost_per_query,
  qs.active_days,
  qs.first_query_date,
  qs.last_query_date,
  ROUND(qs.cache_hits * 100.0 / NULLIF(qs.total_queries, 0), 2) AS cache_hit_pct
FROM
  user_task ut
    JOIN total_task tt
      ON ut.warehouse_identifier = tt.warehouse_identifier
      AND ut.usage_date = tt.usage_date
    JOIN claude_task ct
      ON ut.warehouse_identifier = ct.warehouse_identifier
      AND ut.usage_date = ct.usage_date
    JOIN warehouse_cost wc
      ON ut.warehouse_identifier = wc.warehouse_identifier
      AND ut.usage_date = wc.usage_date
    JOIN query_stats qs
      ON ut.executed_by_identity = qs.executed_by_identity
GROUP BY
  ut.executed_by_identity,
  qs.total_queries,
  qs.active_days,
  qs.first_query_date,
  qs.last_query_date,
  qs.cache_hits
ORDER BY
  estimated_cost_usd DESC
```

**Parameters:** `date_range` (Date Range), `warehouse` (Warehouse), `user` (User)

### `claude_june_avg_daily_cost` — sql_mcp_avg_daily_cost

```sql
WITH warehouse_cost AS (
  SELECT
    o.object_identifier AS warehouse_identifier,
    f.usage_date,
    SUM(f.total_cost) AS total_warehouse_cost_usd
  FROM
    data_automation.databricks_analytics.gold_fact_usage f
      JOIN data_automation.databricks_analytics.gold_dim_object o
        ON f.object_sk = o.object_sk
        AND o.object_type = 'WAREHOUSE'
      JOIN data_automation.databricks_analytics.gold_dim_sku s
        ON f.sku_sk = s.sku_sk
        AND s.sku_name = 'PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST'
  WHERE
    f.usage_date >= DATE_TRUNC('MONTH', CURRENT_DATE())
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, o.object_identifier)
    )
  GROUP BY
    o.object_identifier,
    f.usage_date
),
claude_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS claude_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= DATE_TRUNC('MONTH', CURRENT_DATE())
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
    AND (
      SIZE(:user) = 0
      OR array_contains(:user, executed_by_identity)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
total_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS total_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    query_start_date >= DATE_TRUNC('MONTH', CURRENT_DATE())
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
)
SELECT
  CAST(
    SUM(wc.total_warehouse_cost_usd * ct.claude_task_seconds / NULLIF(tt.total_task_seconds, 0))
      / NULLIF(COUNT(DISTINCT ct.usage_date), 0) AS DECIMAL(18, 4)
  ) AS avg_daily_claude_cost
FROM
  claude_task ct
    JOIN total_task tt
      ON ct.warehouse_identifier = tt.warehouse_identifier
      AND ct.usage_date = tt.usage_date
    JOIN warehouse_cost wc
      ON ct.warehouse_identifier = wc.warehouse_identifier
      AND ct.usage_date = wc.usage_date
```

**Parameters:** `warehouse` (Warehouse), `user` (User)

### `claude_projected_monthly_cost` — sql_mcp_projected_monthly_cost

```sql
WITH warehouse_cost AS (
  SELECT
    o.object_identifier AS warehouse_identifier,
    f.usage_date,
    SUM(f.total_cost) AS total_warehouse_cost_usd
  FROM
    data_automation.databricks_analytics.gold_fact_usage f
      JOIN data_automation.databricks_analytics.gold_dim_object o
        ON f.object_sk = o.object_sk
        AND o.object_type = 'WAREHOUSE'
      JOIN data_automation.databricks_analytics.gold_dim_sku s
        ON f.sku_sk = s.sku_sk
        AND s.sku_name = 'PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST'
  WHERE
    f.usage_date >= DATE_TRUNC('MONTH', CURRENT_DATE())
  GROUP BY
    o.object_identifier,
    f.usage_date
),
claude_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS claude_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= DATE_TRUNC('MONTH', CURRENT_DATE())
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
    AND (
      SIZE(:user) = 0
      OR array_contains(:user, executed_by_identity)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
total_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS total_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    query_start_date >= DATE_TRUNC('MONTH', CURRENT_DATE())
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
daily_avg AS (
  SELECT
    SUM(wc.total_warehouse_cost_usd * ct.claude_task_seconds / NULLIF(tt.total_task_seconds, 0))
      / NULLIF(COUNT(DISTINCT ct.usage_date), 0) AS avg_daily_cost
  FROM
    claude_task ct
      JOIN total_task tt
        ON ct.warehouse_identifier = tt.warehouse_identifier
        AND ct.usage_date = tt.usage_date
      JOIN warehouse_cost wc
        ON ct.warehouse_identifier = wc.warehouse_identifier
        AND ct.usage_date = wc.usage_date
)
SELECT
  CAST(avg_daily_cost * DAY(LAST_DAY(CURRENT_DATE())) AS DECIMAL(18, 2)) AS projected_monthly_cost
FROM
  daily_avg
```

**Parameters:** `warehouse` (Warehouse), `user` (User)

### `claude_pct_share_by_warehouse` — sql_mcp_pct_share_by_warehouse

```sql
SELECT
  COALESCE(q.warehouse_name, g.warehouse_identifier) AS warehouse,
  ROUND(
    SUM(
      CASE
        WHEN
          g.client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
        THEN
          g.total_task_duration_ms
        ELSE 0
      END
    )
      * 100.0
      / NULLIF(SUM(g.total_task_duration_ms), 0),
    2
  ) AS claude_task_pct
FROM
  data_automation.databricks_analytics.gold_query_history g
    LEFT JOIN (
      SELECT DISTINCT
        warehouse_identifier,
        warehouse_name
      FROM
        data_automation.databricks_analytics.gold_query_history
      WHERE
        warehouse_name IS NOT NULL
    ) q
      ON g.warehouse_identifier = q.warehouse_identifier
WHERE
  g.query_start_date >= :date_range.min
  AND g.query_start_date <= :date_range.max
  AND (
    SIZE(:warehouse) = 0
    OR array_contains(:warehouse, g.warehouse_name)
  )
  AND (
    SIZE(:user) = 0
    OR array_contains(:user, g.executed_by_identity)
  )
  AND g.warehouse_identifier IS NOT NULL
GROUP BY
  COALESCE(q.warehouse_name, g.warehouse_identifier)
HAVING
  claude_task_pct > 0
ORDER BY
  claude_task_pct DESC
```

**Parameters:** `date_range` (Date Range), `warehouse` (Warehouse), `user` (User)

### `claude_daily_cost_trend` — sql_mcp_daily_cost_trend

```sql
WITH warehouse_cost AS (
  SELECT
    o.object_identifier AS warehouse_identifier,
    f.usage_date,
    SUM(f.total_cost) AS total_warehouse_cost_usd
  FROM
    data_automation.databricks_analytics.gold_fact_usage f
      JOIN data_automation.databricks_analytics.gold_dim_object o
        ON f.object_sk = o.object_sk
        AND o.object_type = 'WAREHOUSE'
      JOIN data_automation.databricks_analytics.gold_dim_sku s
        ON f.sku_sk = s.sku_sk
        AND s.sku_name = 'PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST'
  WHERE
    f.usage_date >= :date_range.min
    AND f.usage_date <= :date_range.max
  GROUP BY
    o.object_identifier,
    f.usage_date
),
claude_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS claude_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
    AND (
      SIZE(:user) = 0
      OR array_contains(:user, executed_by_identity)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
total_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS total_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
)
SELECT
  ct.usage_date,
  CAST(
    SUM(
      wc.total_warehouse_cost_usd * ct.claude_task_seconds / NULLIF(tt.total_task_seconds, 0)
    ) AS DECIMAL(18, 4)
  ) AS daily_claude_cost
FROM
  claude_task ct
    JOIN total_task tt
      ON ct.warehouse_identifier = tt.warehouse_identifier
      AND ct.usage_date = tt.usage_date
    JOIN warehouse_cost wc
      ON ct.warehouse_identifier = wc.warehouse_identifier
      AND ct.usage_date = wc.usage_date
GROUP BY
  ct.usage_date
ORDER BY
  ct.usage_date
```

**Parameters:** `date_range` (Date Range), `warehouse` (Warehouse), `user` (User)

### `claude_top_10_expensive_days` — sql_mcp_top_10_expensive_days

```sql
WITH warehouse_cost AS (
  SELECT
    o.object_identifier AS warehouse_identifier,
    f.usage_date,
    SUM(f.total_cost) AS total_warehouse_cost_usd
  FROM
    data_automation.databricks_analytics.gold_fact_usage f
      JOIN data_automation.databricks_analytics.gold_dim_object o
        ON f.object_sk = o.object_sk
        AND o.object_type = 'WAREHOUSE'
      JOIN data_automation.databricks_analytics.gold_dim_sku s
        ON f.sku_sk = s.sku_sk
        AND s.sku_name = 'PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST'
  WHERE
    f.usage_date >= :date_range.min
    AND f.usage_date <= :date_range.max
  GROUP BY
    o.object_identifier,
    f.usage_date
),
claude_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS claude_task_seconds,
    COUNT(*) AS total_queries,
    COUNT(DISTINCT executed_by_identity) AS active_users
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
    AND query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
    AND (
      SIZE(:user) = 0
      OR array_contains(:user, executed_by_identity)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
total_task AS (
  SELECT
    warehouse_identifier,
    query_start_date AS usage_date,
    SUM(total_task_duration_ms) / 1000.0 AS total_task_seconds
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    query_start_date >= :date_range.min
    AND query_start_date <= :date_range.max
    AND (
      SIZE(:warehouse) = 0
      OR array_contains(:warehouse, warehouse_name)
    )
  GROUP BY
    warehouse_identifier,
    query_start_date
),
daily AS (
  SELECT
    ct.usage_date,
    SUM(
      wc.total_warehouse_cost_usd * ct.claude_task_seconds / NULLIF(tt.total_task_seconds, 0)
    ) AS claude_cost,
    SUM(ct.total_queries) AS total_queries,
    MAX(ct.active_users) AS active_users
  FROM
    claude_task ct
      JOIN total_task tt
        ON ct.warehouse_identifier = tt.warehouse_identifier
        AND ct.usage_date = tt.usage_date
      JOIN warehouse_cost wc
        ON ct.warehouse_identifier = wc.warehouse_identifier
        AND ct.usage_date = wc.usage_date
  GROUP BY
    ct.usage_date
)
SELECT
  usage_date,
  CAST(claude_cost AS DECIMAL(18, 4)) AS claude_cost,
  total_queries,
  active_users,
  ROUND(claude_cost / NULLIF(total_queries, 0), 4) AS cost_per_query
FROM
  daily
ORDER BY
  claude_cost DESC
LIMIT 10
```

**Parameters:** `date_range` (Date Range), `warehouse` (Warehouse), `user` (User)

### `obj_spend_by_attribution` — obj_spend_by_attribution

```sql
SELECT
  CASE
    WHEN attribution_method = 'UNRESOLVED' THEN 'No Owner Identified'
    ELSE 'Owner Assigned'
  END AS ownership_status,
  CAST(SUM(total_cost) AS DECIMAL(18, 2)) AS total_spend,
  ROUND(SUM(total_cost) * 100.0 / SUM(SUM(total_cost)) OVER (), 2) AS pct_of_total
FROM
  data_automation.databricks_analytics.gold_top_cost_objects_current
WHERE
  (
    SIZE(:object_type) = 0
    OR array_contains(:object_type, object_type)
  )
  AND (
    SIZE(:owner) = 0
    OR array_contains(:owner, COALESCE(owner_identity, 'UNRESOLVED'))
  )
  AND (
    :object_status = 'All'
    OR (
      :object_status = 'Current (Active)'
      AND (
        deleted_indicator = FALSE
        OR deleted_indicator IS NULL
      )
    )
    OR (
      :object_status = 'Historical (Deleted)'
      AND deleted_indicator = TRUE
    )
  )
GROUP BY
  CASE
    WHEN attribution_method = 'UNRESOLVED' THEN 'No Owner Identified'
    ELSE 'Owner Assigned'
  END
```

**Parameters:** `object_type` (Object Type), `owner` (Owner), `object_status` (Object Status)

### `obj_ownership_kpis` — obj_ownership_kpis

```sql
SELECT
  COUNT(*) AS total_objects,
  CAST(
    SUM(
      CASE
        WHEN owner_identity IS NULL THEN total_cost
        ELSE 0
      END
    ) AS DECIMAL(18, 2)
  ) AS unresolved_spend,
  SUM(
    CASE
      WHEN idle_day_count > 90 THEN 1
      ELSE 0
    END
  ) AS idle_objects,
  CAST(
    SUM(
      CASE
        WHEN idle_day_count > 90 THEN total_cost
        ELSE 0
      END
    ) AS DECIMAL(18, 2)
  ) AS idle_cost
FROM
  data_automation.databricks_analytics.gold_top_cost_objects_current
WHERE
  (
    SIZE(:object_type) = 0
    OR array_contains(:object_type, object_type)
  )
  AND (
    SIZE(:owner) = 0
    OR array_contains(:owner, COALESCE(owner_identity, 'UNRESOLVED'))
  )
  AND (
    :object_status = 'All'
    OR (
      :object_status = 'Current (Active)'
      AND (
        deleted_indicator = FALSE
        OR deleted_indicator IS NULL
      )
    )
    OR (
      :object_status = 'Historical (Deleted)'
      AND deleted_indicator = TRUE
    )
  )
```

**Parameters:** `object_type` (Object Type), `owner` (Owner), `object_status` (Object Status)

### `obj_spend_by_owner_top10` — obj_spend_by_owner_top10

```sql
SELECT
  owner_identity AS owner,
  COUNT(DISTINCT object_identifier) AS object_count,
  CAST(SUM(total_cost) AS DECIMAL(18, 2)) AS total_spend,
  ROUND(SUM(total_cost) * 100.0 / SUM(SUM(total_cost)) OVER (), 2) AS pct_of_total
FROM
  data_automation.databricks_analytics.gold_top_cost_objects_current
WHERE
  owner_identity IS NOT NULL
  AND owner_identity LIKE '%@%'
  AND (
    SIZE(:object_type) = 0
    OR array_contains(:object_type, object_type)
  )
  AND (
    SIZE(:owner) = 0
    OR array_contains(:owner, COALESCE(owner_identity, 'UNRESOLVED'))
  )
  AND (
    :object_status = 'All'
    OR (
      :object_status = 'Current (Active)'
      AND (
        deleted_indicator = FALSE
        OR deleted_indicator IS NULL
      )
    )
    OR (
      :object_status = 'Historical (Deleted)'
      AND deleted_indicator = TRUE
    )
  )
GROUP BY
  owner_identity
ORDER BY
  total_spend DESC
LIMIT 10
```

**Parameters:** `object_type` (Object Type), `owner` (Owner), `object_status` (Object Status)

### `obj_full_list` — obj_full_list

```sql
SELECT
  cost_rank,
  object_type,
  COALESCE(object_name, object_identifier) AS object_name,
  COALESCE(owner_identity, 'UNRESOLVED') AS owner,
  attribution_method,
  COALESCE(workspace_name, 'Decommissioned') AS workspace_name,
  CAST(total_cost AS DECIMAL(18, 2)) AS total_spend,
  last_activity_date,
  idle_day_count
FROM
  data_automation.databricks_analytics.gold_top_cost_objects_current
WHERE
  (
    SIZE(:object_type) = 0
    OR array_contains(:object_type, object_type)
  )
  AND (
    SIZE(:owner) = 0
    OR array_contains(:owner, COALESCE(owner_identity, 'UNRESOLVED'))
  )
  AND (
    :object_status = 'All'
    OR (
      :object_status = 'Current (Active)'
      AND (
        deleted_indicator = FALSE
        OR deleted_indicator IS NULL
      )
    )
    OR (
      :object_status = 'Historical (Deleted)'
      AND deleted_indicator = TRUE
    )
  )
ORDER BY
  total_cost DESC
```

**Parameters:** `object_type` (Object Type), `owner` (Owner), `object_status` (Object Status)

### `obj_spend_by_type` — obj_spend_by_type

```sql
SELECT
  object_type,
  CAST(SUM(total_cost) AS DECIMAL(18, 2)) AS total_spend,
  ROUND(SUM(total_cost) * 100.0 / NULLIF(SUM(SUM(total_cost)) OVER (), 0), 1) AS pct_of_total,
  COUNT(*) AS object_count
FROM
  data_automation.databricks_analytics.gold_top_cost_objects_current
WHERE
  (
    SIZE(:object_type) = 0
    OR array_contains(:object_type, object_type)
  )
  AND (
    SIZE(:owner) = 0
    OR array_contains(:owner, COALESCE(owner_identity, 'UNRESOLVED'))
  )
  AND (
    :object_status = 'All'
    OR (
      :object_status = 'Current (Active)'
      AND (
        deleted_indicator = FALSE
        OR deleted_indicator IS NULL
      )
    )
    OR (
      :object_status = 'Historical (Deleted)'
      AND deleted_indicator = TRUE
    )
  )
GROUP BY
  object_type
ORDER BY
  total_spend DESC
```

**Parameters:** `object_type` (Object Type), `owner` (Owner), `object_status` (Object Status)

### `obj_idle_by_type` — obj_idle_by_type

```sql
SELECT
  object_type,
  COUNT(*) AS idle_count,
  CAST(SUM(total_cost) AS DECIMAL(18, 2)) AS idle_spend
FROM
  data_automation.databricks_analytics.gold_top_cost_objects_current
WHERE
  idle_day_count > 90
  AND (
    SIZE(:object_type) = 0
    OR array_contains(:object_type, object_type)
  )
  AND (
    SIZE(:owner) = 0
    OR array_contains(:owner, COALESCE(owner_identity, 'UNRESOLVED'))
  )
  AND (
    :object_status = 'All'
    OR (
      :object_status = 'Current (Active)'
      AND (
        deleted_indicator = FALSE
        OR deleted_indicator IS NULL
      )
    )
    OR (
      :object_status = 'Historical (Deleted)'
      AND deleted_indicator = TRUE
    )
  )
GROUP BY
  object_type
ORDER BY
  idle_spend DESC
```

**Parameters:** `object_type` (Object Type), `owner` (Owner), `object_status` (Object Status)

### `obj_owner_options` — obj_owner_options

```sql
SELECT DISTINCT
  COALESCE(owner_identity, 'UNRESOLVED') AS owner_identity
FROM
  data_automation.databricks_analytics.gold_top_cost_objects_current
ORDER BY
  owner_identity
```

### `tag_kpis` — Tag KPIs

```sql
SELECT
  CAST(SUM(total_cost) AS DECIMAL(18, 2)) AS total_spend,
  ROUND(
    SUM(
      CASE
        WHEN tag_team_text != 'UNTAGGED' THEN total_cost
        ELSE 0
      END
    )
      * 100.0
      / NULLIF(SUM(total_cost), 0),
    1
  ) AS team_tag_coverage_pct,
  CAST(
    SUM(
      CASE
        WHEN tag_team_text = 'UNTAGGED' THEN total_cost
        ELSE 0
      END
    ) AS DECIMAL(18, 2)
  ) AS untagged_spend,
  COUNT(DISTINCT
    CASE
      WHEN tag_team_text != 'UNTAGGED' THEN tag_team_text
    END
  ) AS unique_teams
FROM
  data_automation.databricks_analytics.gold_fact_usage
WHERE
  usage_date >= :date_range.min
  AND usage_date <= :date_range.max
  AND (
    SIZE(:team) = 0
    OR array_contains(:team, tag_team_text)
  )
  AND (
    SIZE(:domain) = 0
    OR array_contains(:domain, tag_domain_text)
  )
  AND (
    SIZE(:purpose) = 0
    OR array_contains(:purpose, tag_purpose_text)
  )
```

**Parameters:** `date_range` (Date Range), `team` (Team), `domain` (Domain), `purpose` (Purpose)

### `tag_coverage_monthly` — Tag Coverage Monthly

```sql
SELECT
  DATE_TRUNC('MONTH', usage_date) AS month,
  ROUND(
    SUM(
      CASE
        WHEN tag_team_text != 'UNTAGGED' THEN total_cost
        ELSE 0
      END
    )
      * 100.0
      / NULLIF(SUM(total_cost), 0),
    1
  ) AS team_coverage_pct,
  ROUND(
    SUM(
      CASE
        WHEN tag_domain_text != 'UNTAGGED' THEN total_cost
        ELSE 0
      END
    )
      * 100.0
      / NULLIF(SUM(total_cost), 0),
    1
  ) AS domain_coverage_pct,
  ROUND(
    SUM(
      CASE
        WHEN tag_purpose_text != 'UNTAGGED' THEN total_cost
        ELSE 0
      END
    )
      * 100.0
      / NULLIF(SUM(total_cost), 0),
    1
  ) AS purpose_coverage_pct
FROM
  data_automation.databricks_analytics.gold_fact_usage
WHERE
  usage_date >= :date_range.min
  AND usage_date <= :date_range.max
  AND (
    SIZE(:team) = 0
    OR array_contains(:team, tag_team_text)
  )
  AND (
    SIZE(:domain) = 0
    OR array_contains(:domain, tag_domain_text)
  )
  AND (
    SIZE(:purpose) = 0
    OR array_contains(:purpose, tag_purpose_text)
  )
GROUP BY
  DATE_TRUNC('MONTH', usage_date)
ORDER BY
  month
```

**Parameters:** `date_range` (Date Range), `team` (Team), `domain` (Domain), `purpose` (Purpose)

### `tag_spend_by_domain` — Tag Spend by Domain

```sql
SELECT
  tag_domain_text AS domain,
  CAST(SUM(total_cost) AS DECIMAL(18, 2)) AS spend
FROM
  data_automation.databricks_analytics.gold_fact_usage
WHERE
  usage_date >= :date_range.min
  AND usage_date <= :date_range.max
  AND (
    SIZE(:team) = 0
    OR array_contains(:team, tag_team_text)
  )
  AND (
    SIZE(:domain) = 0
    OR array_contains(:domain, tag_domain_text)
  )
  AND (
    SIZE(:purpose) = 0
    OR array_contains(:purpose, tag_purpose_text)
  )
GROUP BY
  tag_domain_text
ORDER BY
  spend DESC
```

**Parameters:** `date_range` (Date Range), `team` (Team), `domain` (Domain), `purpose` (Purpose)

### `tag_spend_by_purpose` — Tag Spend by Purpose

```sql
SELECT
  tag_purpose_text AS purpose,
  CAST(SUM(total_cost) AS DECIMAL(18, 2)) AS spend
FROM
  data_automation.databricks_analytics.gold_fact_usage
WHERE
  usage_date >= :date_range.min
  AND usage_date <= :date_range.max
  AND (
    SIZE(:team) = 0
    OR array_contains(:team, tag_team_text)
  )
  AND (
    SIZE(:domain) = 0
    OR array_contains(:domain, tag_domain_text)
  )
  AND (
    SIZE(:purpose) = 0
    OR array_contains(:purpose, tag_purpose_text)
  )
GROUP BY
  tag_purpose_text
ORDER BY
  spend DESC
```

**Parameters:** `date_range` (Date Range), `team` (Team), `domain` (Domain), `purpose` (Purpose)

### `tag_spend_by_team` — Tag Spend by Team

```sql
SELECT
  tag_team_text AS team,
  CAST(SUM(total_cost) AS DECIMAL(18, 2)) AS spend
FROM
  data_automation.databricks_analytics.gold_fact_usage
WHERE
  usage_date >= :date_range.min
  AND usage_date <= :date_range.max
  AND (
    SIZE(:team) = 0
    OR array_contains(:team, tag_team_text)
  )
  AND (
    SIZE(:domain) = 0
    OR array_contains(:domain, tag_domain_text)
  )
  AND (
    SIZE(:purpose) = 0
    OR array_contains(:purpose, tag_purpose_text)
  )
GROUP BY
  tag_team_text
ORDER BY
  spend DESC
```

**Parameters:** `date_range` (Date Range), `team` (Team), `domain` (Domain), `purpose` (Purpose)

### `tag_domain_options` — tag_domain_options

```sql
SELECT DISTINCT
  tag_domain_text AS domain
FROM
  data_automation.databricks_analytics.gold_fact_usage
WHERE
  tag_domain_text IS NOT NULL
ORDER BY
  domain
```

### `tag_team_options` — tag_team_options

```sql
SELECT DISTINCT
  tag_team_text AS team
FROM
  data_automation.databricks_analytics.gold_fact_usage
WHERE
  tag_team_text IS NOT NULL
ORDER BY
  team
```

### `tag_detail` — Tag Detail Table

```sql
SELECT
  tag_team_text AS team,
  tag_domain_text AS domain,
  tag_purpose_text AS purpose,
  CAST(SUM(total_cost) AS DECIMAL(18, 2)) AS total_spend,
  COUNT(DISTINCT usage_date) AS active_days,
  ROUND(SUM(total_cost) * 100.0 / NULLIF(SUM(SUM(total_cost)) OVER (), 0), 2) AS pct_of_total
FROM
  data_automation.databricks_analytics.gold_fact_usage
WHERE
  usage_date >= :date_range.min
  AND usage_date <= :date_range.max
  AND (
    SIZE(:team) = 0
    OR array_contains(:team, tag_team_text)
  )
  AND (
    SIZE(:domain) = 0
    OR array_contains(:domain, tag_domain_text)
  )
  AND (
    SIZE(:purpose) = 0
    OR array_contains(:purpose, tag_purpose_text)
  )
GROUP BY
  tag_team_text,
  tag_domain_text,
  tag_purpose_text
ORDER BY
  total_spend DESC
```

**Parameters:** `date_range` (Date Range), `team` (Team), `domain` (Domain), `purpose` (Purpose)

### `tag_untagged_by_product` — Tag Untagged by Product

```sql
SELECT
  sk.billing_origin_product AS product,
  CAST(SUM(f.total_cost) AS DECIMAL(18, 2)) AS untagged_spend
FROM
  data_automation.databricks_analytics.gold_fact_usage f
    JOIN data_automation.databricks_analytics.gold_dim_sku sk
      ON f.sku_sk = sk.sku_sk
WHERE
  f.tag_team_text = 'UNTAGGED'
  AND f.usage_date >= :date_range.min
  AND f.usage_date <= :date_range.max
  AND (
    SIZE(:team) = 0
    OR array_contains(:team, f.tag_team_text)
  )
  AND (
    SIZE(:domain) = 0
    OR array_contains(:domain, f.tag_domain_text)
  )
  AND (
    SIZE(:purpose) = 0
    OR array_contains(:purpose, f.tag_purpose_text)
  )
GROUP BY
  sk.billing_origin_product
ORDER BY
  untagged_spend DESC
```

**Parameters:** `date_range` (Date Range), `team` (Team), `domain` (Domain), `purpose` (Purpose)

### `tag_purpose_options` — tag_purpose_options

```sql
SELECT DISTINCT
  tag_purpose_text AS purpose
FROM
  data_automation.databricks_analytics.gold_fact_usage
WHERE
  tag_purpose_text IS NOT NULL
ORDER BY
  purpose
```

### `obj_status_options` — obj_status_options

```sql
SELECT
  'All' AS object_status
UNION ALL
SELECT
  'Current (Active)'
UNION ALL
SELECT
  'Historical (Deleted)'
```

### `obj_top10_unresolved` — obj_top10_unresolved

```sql
SELECT
  object_type,
  COALESCE(object_name, object_identifier) AS object_name,
  CAST(total_cost AS DECIMAL(18, 2)) AS total_spend,
  last_activity_date,
  idle_day_count,
  COALESCE(workspace_name, 'Decommissioned') AS workspace_name
FROM
  data_automation.databricks_analytics.gold_top_cost_objects_current
WHERE
  owner_identity IS NULL
  AND (
    SIZE(:object_type) = 0
    OR array_contains(:object_type, object_type)
  )
  AND (
    SIZE(:owner) = 0
    OR array_contains(:owner, COALESCE(owner_identity, 'UNRESOLVED'))
  )
  AND (
    :object_status = 'All'
    OR (
      :object_status = 'Current (Active)'
      AND (
        deleted_indicator = FALSE
        OR deleted_indicator IS NULL
      )
    )
    OR (
      :object_status = 'Historical (Deleted)'
      AND deleted_indicator = TRUE
    )
  )
ORDER BY
  total_cost DESC
LIMIT 10
```

**Parameters:** `object_type` (Object Type), `owner` (Owner), `object_status` (Object Status)

### `claude_daily_volume_top5_users` — SQL MCP Daily Volume Top 5 Users

```sql
WITH top5 AS (
  SELECT
    executed_by_identity
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
  GROUP BY
    executed_by_identity
  ORDER BY
    COUNT(*) DESC
  LIMIT 5
)
SELECT
  q.query_start_date AS date,
  q.executed_by_identity AS user,
  COUNT(*) AS query_count
FROM
  data_automation.databricks_analytics.gold_query_history q
    JOIN top5 t
      ON q.executed_by_identity = t.executed_by_identity
WHERE
  q.client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
GROUP BY
  q.query_start_date,
  q.executed_by_identity
ORDER BY
  date,
  query_count DESC
```

### `domain_tag_coverage_pct` — Domain Tag Coverage Pct

```sql
SELECT
  ROUND(
    SUM(
      CASE
        WHEN tag_domain_text != 'UNTAGGED' THEN total_cost
        ELSE 0
      END
    )
      * 100.0
      / NULLIF(SUM(total_cost), 0),
    2
  ) AS domain_coverage_pct
FROM
  data_automation.databricks_analytics.gold_fact_usage
WHERE
  usage_date >= :date_range.min
  AND usage_date <= :date_range.max
  AND (
    SIZE(:team) = 0
    OR array_contains(:team, tag_team_text)
  )
  AND (
    SIZE(:domain) = 0
    OR array_contains(:domain, tag_domain_text)
  )
  AND (
    SIZE(:purpose) = 0
    OR array_contains(:purpose, tag_purpose_text)
  )
```

**Parameters:** `date_range` (Date Range), `team` (Team), `domain` (Domain), `purpose` (Purpose)

### `purpose_tag_coverage_pct` — Purpose Tag Coverage Pct

```sql
SELECT
  ROUND(
    SUM(
      CASE
        WHEN tag_purpose_text != 'UNTAGGED' THEN total_cost
        ELSE 0
      END
    )
      * 100.0
      / NULLIF(SUM(total_cost), 0),
    2
  ) AS purpose_coverage_pct
FROM
  data_automation.databricks_analytics.gold_fact_usage
WHERE
  usage_date >= :date_range.min
  AND usage_date <= :date_range.max
  AND (
    SIZE(:team) = 0
    OR array_contains(:team, tag_team_text)
  )
  AND (
    SIZE(:domain) = 0
    OR array_contains(:domain, tag_domain_text)
  )
  AND (
    SIZE(:purpose) = 0
    OR array_contains(:purpose, tag_purpose_text)
  )
```

**Parameters:** `date_range` (Date Range), `team` (Team), `domain` (Domain), `purpose` (Purpose)

### `claude_query_volume_by_user_month` — SQL MCP Query Volume by User and Month

```sql
WITH top10 AS (
  SELECT
    executed_by_identity
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
  GROUP BY
    executed_by_identity
  ORDER BY
    COUNT(*) DESC
  LIMIT 10
)
SELECT
  q.executed_by_identity AS user,
  SUM(
    CASE
      WHEN DATE_TRUNC('MONTH', q.query_start_date) = '2026-02-01' THEN 1
      ELSE 0
    END
  ) AS feb_2026,
  SUM(
    CASE
      WHEN DATE_TRUNC('MONTH', q.query_start_date) = '2026-03-01' THEN 1
      ELSE 0
    END
  ) AS mar_2026,
  SUM(
    CASE
      WHEN DATE_TRUNC('MONTH', q.query_start_date) = '2026-04-01' THEN 1
      ELSE 0
    END
  ) AS apr_2026,
  SUM(
    CASE
      WHEN DATE_TRUNC('MONTH', q.query_start_date) = '2026-05-01' THEN 1
      ELSE 0
    END
  ) AS may_2026,
  SUM(
    CASE
      WHEN DATE_TRUNC('MONTH', q.query_start_date) = '2026-06-01' THEN 1
      ELSE 0
    END
  ) AS jun_2026,
  COUNT(*) AS total_queries
FROM
  data_automation.databricks_analytics.gold_query_history q
    JOIN top10 t
      ON q.executed_by_identity = t.executed_by_identity
WHERE
  q.client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
GROUP BY
  q.executed_by_identity
ORDER BY
  total_queries DESC
```

### `claude_query_volume_heatmap` — SQL MCP Query Volume Heatmap

```sql
WITH top10 AS (
  SELECT
    executed_by_identity
  FROM
    data_automation.databricks_analytics.gold_query_history
  WHERE
    client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
  GROUP BY
    executed_by_identity
  ORDER BY
    COUNT(*) DESC
  LIMIT 10
),
base AS (
  SELECT
    q.executed_by_identity AS user,
    DATE_TRUNC('MONTH', q.query_start_date) AS month,
    COUNT(*) AS query_count
  FROM
    data_automation.databricks_analytics.gold_query_history q
      JOIN top10 t
        ON q.executed_by_identity = t.executed_by_identity
  WHERE
    q.client_application IN ('Databricks SQL MCP', 'DatabricksDbsqlMcp')
  GROUP BY
    q.executed_by_identity,
    DATE_TRUNC('MONTH', q.query_start_date)
)
SELECT
  user,
  DATE_FORMAT(month, 'MMM yyyy') AS month_label,
  month AS month_sort,
  query_count
FROM
  base
ORDER BY
  month_sort,
  query_count DESC
```

### `e95af4d2` — Cost by App

```sql
WITH app_usage AS (
  SELECT
    u.usage_date,
    u.usage_metadata.app_name AS app_name,
    u.usage_metadata.app_id AS app_id,
    u.identity_metadata.created_by AS owner,
    u.product_features.apps.compute_size AS compute_size,
    u.usage_quantity,
    u.usage_quantity * lp.pricing.default AS cost_usd
  FROM system.billing.usage u
  JOIN system.billing.list_prices lp
    ON u.sku_name = lp.sku_name
    AND u.usage_start_time >= lp.price_start_time
    AND (lp.price_end_time IS NULL OR u.usage_start_time < lp.price_end_time)
  WHERE u.billing_origin_product = 'APPS'
    AND u.usage_date BETWEEN :filter_date_range.min AND :filter_date_range.max
)
SELECT
  app_name,
  owner,
  compute_size,
  COUNT(DISTINCT usage_date)   AS active_days,
  SUM(usage_quantity)          AS total_dbus,
  SUM(cost_usd)                AS total_cost_usd
FROM app_usage
GROUP BY app_name, owner, compute_size
ORDER BY total_cost_usd DESC
```

**Parameters:** `filter_date_range` (filter_date_range)

### `125a56d0` — Application Daily Cost Summary Report

```sql
WITH app_usage AS (
  SELECT
    u.usage_date,
    u.usage_metadata.app_name AS app_name,
    u.usage_metadata.app_id AS app_id,
    u.identity_metadata.created_by AS owner,
    u.product_features.apps.compute_size AS compute_size,
    u.usage_quantity,
    u.usage_quantity * lp.pricing.default AS cost_usd
  FROM system.billing.usage u
  JOIN system.billing.list_prices lp
    ON u.sku_name = lp.sku_name
    AND u.usage_start_time >= lp.price_start_time
    AND (lp.price_end_time IS NULL OR u.usage_start_time < lp.price_end_time)
  WHERE u.billing_origin_product = 'APPS'
    AND u.usage_date BETWEEN :filter_date_range.min AND :filter_date_range.max
)
SELECT usage_date, app_name, SUM(cost_usd) AS daily_cost_usd
FROM app_usage
GROUP BY usage_date, app_name
ORDER BY usage_date
```

**Parameters:** `filter_date_range` (filter_date_range)
