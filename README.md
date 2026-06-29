# Supply Chain Performance & Risk Intelligence Dashboard

> **An end-to-end analytics solution that transforms raw supply chain data into actionable decisions — built with Python, SQL, and Power BI.**

---

## The Business Problem

Supply chain leaders often operate without a unified view of what's working and what's costing them money. Delayed shipments go undetected until they become customer complaints. High-defect suppliers continue to receive orders. Shipping routes with poor on-time rates keep getting used because no one has compared them side by side.

This project addresses that gap. It answers three critical business questions:

- **Which suppliers are putting delivery performance at risk — and by how much?**
- **Which products and customer segments are generating the most profit — and which are underperforming?**
- **Which shipping modes and carriers offer the best balance of speed, cost, and reliability?**

The dashboard is designed so that a supply chain manager, operations director, or C-suite executive can open it, apply a single filter, and walk away with a decision in under 60 seconds.

---

## Key Business Insights

| Insight | Finding | Recommended Action |
|---|---|---|
| OTD Rate is 83% against an 85% target | 17 orders delayed, avg 0.6 days late | Audit Carrier A Rail routes — lowest OTD at 57% |
| Supplier 5 has the highest defect rate (2.7%) | 26 SKUs flagged as High Risk | Consider supplier audit or secondary sourcing |
| Skincare drives 41% of total revenue | Highest margin product type at 91.6% | Prioritise Skincare inventory and fulfilment |
| Air + Carrier C achieves 100% OTD | Zero delay days, cost of $38 per shipment | Expand Air/Carrier C usage for high-value SKUs |
| Female segment drives highest revenue across all product types | $79K in Skincare alone | Target Female demographic in marketing strategy |

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Data Cleaning & EDA | Python (Pandas, NumPy, Matplotlib) | Profile, clean, engineer features |
| Dimensional Modeling | Python (Pandas) | Build star schema tables |
| Analytical Layer | SQLite (via Python) | Write production-grade SQL views |
| Visualisation | Power BI (DAX, RLS, Star Schema) | 2-page interactive dashboard |
| Version Control | GitHub | Portfolio hosting |

---

## Project Structure

```
supply-chain-analytics/
│
├── data/
│   ├── raw/
│   │   └── supply_chain_data.csv          ← original Kaggle dataset
│   └── processed/
│       ├── supply_chain_clean.csv          ← cleaned & feature-engineered
│       └── star_schema/
│           ├── dim_product.csv
│           ├── dim_supplier.csv
│           ├── dim_shipping.csv
│           ├── dim_customer.csv
│           ├── dim_inspection.csv
│           ├── fact_supply_chain.csv
│           ├── vw_supplier_scorecard.csv
│           ├── vw_product_profitability.csv
│           ├── vw_shipping_efficiency.csv
│           └── vw_quality_risk.csv
│
├── python/
│   ├── 01_eda_cleaning.py                 ← EDA, cleaning, feature engineering
│   └── 02_feature_engineering.py          ← dimensional modeling (star schema)
│
├── sql/
│   └── 03_analytical_views.py             ← SQL analytical views via SQLite
│
├── powerbi/
│   └── SupplyChainDashboard.pbix          ← Power BI dashboard file
│
├── assets/
│   └── screenshots/
│       ├── page1_executive_overview.png
│       └── page2_operations_deepdive.png
│
└── README.md
```

---

## Dashboard Pages

### Page 1 — Executive Overview
*For: Supply chain directors, C-suite, senior leadership*

![Executive Overview](assets/screenshots/page1_executive_overview.png)

**What it shows:**
- 5 KPI cards: Total Revenue, Gross Profit, OTD Rate %, Profit Margin %, Avg Defect Rate %
- Revenue breakdown by product type — instantly shows which products drive the business
- OTD Split donut — shows the on-time vs delayed split at a glance
- Defect Risk Tier donut — flags the proportion of High/Medium/Low risk SKUs
- Profit Margin trend by product type — identifies where margin is being eroded
- Defect Rate by Supplier — signals which suppliers need attention

**Decision it enables:** A director can open this page and immediately know whether the business is hitting delivery targets, which product lines are most profitable, and which suppliers are creating quality risk — without asking anyone for a report.

---

### Page 2 — Operations Deep Dive
*For: Operations managers, logistics teams, procurement analysts*

![Operations Deep Dive](assets/screenshots/page2_operations_deepdive.png)

**What it shows:**
- OTD Rate vs 85% Target gauge — live performance tracking against goal
- Top Suppliers by Revenue — prioritises which supplier relationships matter most
- Shipping Mode Efficiency table — with conditional formatting (🔴 red = below 70% OTD, 🟡 amber = 70–85%, 🟢 green = above 85%)
- Revenue by Product & Customer Segment treemap — reveals which product/customer combinations drive the most value

**Decision it enables:** An operations manager can filter by a specific carrier or transport mode and immediately see its OTD rate, average delay, and shipping cost — then decide whether to renegotiate, switch carriers, or escalate to leadership.

---

## Data Pipeline

```
Raw CSV (100 rows × 24 columns)
    │
    ▼
Python — EDA & Cleaning (01_eda_cleaning.py)
    • Standardised column names to snake_case
    • Fixed data types across all numeric columns
    • Standardised categorical values (title case)
    • Engineered 8 new KPI columns:
        - profit_margin_pct
        - on_time_flag
        - delay_days
        - defect_risk_tier (Low / Medium / High)
        - revenue_per_unit
        - stock_health (Critical / Watch / Healthy)
        - total_cost
        - cost_efficiency_pct
    │
    ▼
Python — Dimensional Modeling (02_feature_engineering.py)
    • Split flat table into star schema:
        - dim_product    (100 rows)
        - dim_supplier   (25 rows)
        - dim_shipping   (33 rows)
        - dim_customer   (4 rows)
        - dim_inspection (3 rows)
        - fact_supply_chain (100 rows)
    • Validated zero null keys across all joins
    │
    ▼
SQLite — Analytical Views (03_analytical_views.py)
    • vw_supplier_scorecard    — OTD, delay, defect, risk tier per supplier
    • vw_product_profitability — revenue, cost, margin per SKU
    • vw_shipping_efficiency   — OTD, cost, speed per carrier + mode + route
    • vw_quality_risk          — defect analysis with CTE and CASE logic
    │
    ▼
Power BI — Interactive Dashboard
    • Star schema relationships in Model View
    • 13 DAX measures in dedicated _Measures table
    • Conditional formatting on OTD Rate %
    • Synced slicers across both pages
    • Page navigation buttons
```

---

## DAX Measures (Key Examples)

```dax
-- On-Time Delivery Rate
OTD Rate % =
ROUND(
    DIVIDE(
        SUM(fact_supply_chain[on_time_flag]),
        COUNTROWS(fact_supply_chain), 0
    ) * 100, 1)

-- Dynamic status label for KPI cards
OTD Status =
IF([OTD Rate %] >= 85, "✅ On Track",
   IF([OTD Rate %] >= 70, "⚠️ At Risk", "🔴 Critical"))

-- Profit Margin %
Profit Margin % =
ROUND(DIVIDE([Gross Profit], [Total Revenue], 0) * 100, 2)

-- Supplier Revenue Ranking
Supplier Revenue Rank =
RANKX(
    ALL(dim_supplier[supplier_name]),
    [Total Revenue], , DESC, DENSE)
```

---

## SQL Analytical Views (Key Example)

```sql
-- Supplier Performance Scorecard
SELECT
    s.supplier_name,
    s.location,
    COUNT(*)                                       AS total_orders,
    ROUND(AVG(f.on_time_flag) * 100, 1)           AS otd_rate_pct,
    ROUND(AVG(f.delay_days), 1)                    AS avg_delay_days,
    ROUND(AVG(f.defect_rates), 4)                  AS avg_defect_rate,
    CASE
        WHEN AVG(f.on_time_flag) * 100 >= 85 THEN 'Low Risk'
        WHEN AVG(f.on_time_flag) * 100 >= 70 THEN 'Medium Risk'
        ELSE 'High Risk'
    END                                            AS supplier_risk_tier
FROM fact_supply_chain f
JOIN dim_supplier s ON f.supplier_key = s.supplier_key
GROUP BY s.supplier_name, s.location
ORDER BY otd_rate_pct DESC
```

---

## Dataset

- **Source:** [Supply Chain Analysis — Kaggle](https://www.kaggle.com/datasets/harshsingh2209/supply-chain-analysis)
- **Size:** 100 rows × 24 columns (raw) → 100 rows × 32 columns (cleaned)
- **Domain:** Beauty & personal care supply chain (Skincare, Haircare, Cosmetics)
- **Coverage:** 5 suppliers, 3 transport modes, 3 carriers, 3 product types, 4 customer segments

---

## How to Run This Project

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/supply-chain-analytics.git
cd supply-chain-analytics
```

**2. Install dependencies**
```bash
pip install pandas numpy matplotlib seaborn sqlalchemy
```

**3. Run Python scripts in order**
```bash
python python/01_eda_cleaning.py
python python/02_feature_engineering.py
python python/03_analytical_views.py
```

**4. Open the dashboard**
- Open `powerbi/SupplyChainDashboard.pbix` in Power BI Desktop
- All data connections point to the local `data/processed/star_schema/` folder

---

## About

Built by **Sreeja Podduturi** — Data Analyst with 3+ years of experience in financial services and healthcare analytics.

- 💼 [LinkedIn](www.linkedin.com/in/sreeja-podduturi-733a58319)
- 📁 [GitHub](https://github.com/yourusername)
- 📧 podduturisreejar@gmail.com
