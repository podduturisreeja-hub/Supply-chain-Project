# Supply Chain Performance & Risk Intelligence Dashboard

An end-to-end analytics project that transforms raw supply chain data into actionable business decisions — built with Python, SQL, and Power BI.

---

## Why This Dataset?

This project uses a publicly available synthetic supply chain dataset that intentionally covers multiple industries rather than one specific company. That was a deliberate choice — supply chain KPIs like On-Time Delivery, Defect Rates, Supplier Risk, and Shipping Efficiency follow the same analytical patterns whether you're in retail, manufacturing, FMCG, or logistics. The goal was to demonstrate those patterns clearly, not to analyze one company's proprietary data.

---

## Business Questions This Project Answers

- Which suppliers are consistently missing delivery targets — and how much is that costing the business?
- Which product types generate the highest revenue and profit margin?
- Which shipping modes and carriers offer the best balance of speed, reliability, and cost?
- Where are quality defects concentrated — by supplier, product, or inspection outcome?
- Which customer segments drive the most revenue across product lines?

---

## What the Data Revealed

| Finding | Impact |
|---|---|
| OTD Rate sitting at 83% against an 85% target | 17 orders delayed — Carrier A Rail routes are the main cause at 57% OTD |
| Supplier 5 has the highest defect rate at 2.7% | 26 SKUs flagged High Risk — needs supplier audit or secondary sourcing |
| Skincare drives 41% of total revenue | Highest margin product — should be prioritised in inventory and fulfilment |
| Air + Carrier C achieves 100% OTD at $38 avg shipping cost | Best performing route — should be expanded for high-value SKUs |
| Road + Carrier B has 90.9% OTD at lower cost than Air | Strong alternative for cost-sensitive shipments |

---

## Decisions This Dashboard Enables

**For Operations Managers:**
Filter by transport mode in the Shipping Efficiency table — instantly see OTD rate, average delay, and cost side by side. Use this to decide whether to renegotiate with a carrier or switch routes entirely.

**For Supply Chain Directors:**
The Supplier Risk findings show which supplier relationships need immediate attention vs which are performing well — without needing to pull a single report manually.

**For Product & Sales Teams:**
The Revenue by Product & Customer Segment treemap shows which product-demographic combinations drive the most value — useful for prioritising stock allocation and marketing spend.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data Cleaning & EDA | Python (Pandas, NumPy, Matplotlib, Seaborn) |
| Dimensional Modeling | Python (star schema — 5 dim tables + 1 fact table) |
| Analytical Layer | SQL (SQLite — 4 production-grade analytical views) |
| Dashboard | Power BI (DAX, conditional formatting, synced slicers, star schema) |

---

## Key DAX Measures

```dax
OTD Rate % =
ROUND(
    DIVIDE(SUM(fact_supply_chain[on_time_flag]),
           COUNTROWS(fact_supply_chain), 0) * 100, 1)

OTD Status =
IF([OTD Rate %] >= 85, "✅ On Track",
   IF([OTD Rate %] >= 70, "⚠️ At Risk", "🔴 Critical"))

Profit Margin % =
ROUND(DIVIDE([Gross Profit], [Total Revenue], 0) * 100, 2)
```

---

## Key SQL View (Supplier Scorecard)

```sql
SELECT
    s.supplier_name,
    s.location,
    ROUND(AVG(f.on_time_flag) * 100, 1)  AS otd_rate_pct,
    ROUND(AVG(f.delay_days), 1)           AS avg_delay_days,
    ROUND(AVG(f.defect_rates), 4)         AS avg_defect_rate,
    CASE
        WHEN AVG(f.on_time_flag) * 100 >= 85 THEN 'Low Risk'
        WHEN AVG(f.on_time_flag) * 100 >= 70 THEN 'Medium Risk'
        ELSE 'High Risk'
    END AS supplier_risk_tier
FROM fact_supply_chain f
JOIN dim_supplier s ON f.supplier_key = s.supplier_key
GROUP BY s.supplier_name, s.location
ORDER BY otd_rate_pct DESC;
```

---

## Dataset
- **Source:** [Kaggle — Supply Chain Analysis](https://www.kaggle.com/datasets/harshsingh2209/supply-chain-analysis)
- **Size:** 100 rows × 24 columns (raw) → 32 columns after feature engineering
- **Coverage:** 5 suppliers, 3 transport modes, 3 carriers, 3 product types, 4 customer segments

---

## Author
**Sreeja Podduturi** — Data Analyst | Power BI | SQL | Python  
📧 podduturisreejar@gmail.com | [LinkedIn](https://www.linkedin.com/in/sreeja-podduturi-733a58319/) | [GitHub](https://github.com/podduturisreeja-hub)
