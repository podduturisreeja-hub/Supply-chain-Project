# =============================================================================
# Supply Chain Analytics — Phase 1: EDA & Data Cleaning
# Author  : Sreeja Podduturi
# Dataset : supply_chain_data.csv (100 rows × 24 columns)
# Purpose : Understand the raw data, clean it, engineer new features,
#           and export a production-ready cleaned file for SQL loading.
# =============================================================================

# ── 0. IMPORTS ────────────────────────────────────────────────────────────────
# pandas  → tabular data manipulation (your main workhorse)
# numpy   → numerical operations & conditional logic
# matplotlib/seaborn → quick visual checks during cleaning

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Makes plots look clean in Jupyter notebooks
%matplotlib inline
sns.set_theme(style="whitegrid", palette="muted")

print("Libraries loaded")


# =============================================================================
# SECTION 1 — LOAD & FIRST LOOK
# Goal: Understand what we're working with before touching anything.
# =============================================================================

df = pd.read_csv('../data/raw/supply_chain_data.csv')

# .shape → (rows, columns) — always the first thing to check
print(f"\n Shape: {df.shape}")           # (100, 24)

# .head() → see the first 5 rows to understand layout
print("\n First 3 rows:")
print(df.head(3).to_string())

# .dtypes → data types of every column
# int64 = whole numbers, float64 = decimals, object = text/string
print("\n Data types:")
print(df.dtypes)

# .isnull().sum() → count missing values per column
print("\n Missing values per column:")
print(df.isnull().sum())

# .duplicated().sum() → count fully duplicate rows
print(f"\n Duplicate rows: {df.duplicated().sum()}")

# KEY OBSERVATION from the profile run:
#   - No nulls, no duplicates in this dataset
#   - Two columns named similarly: 'Lead times' and 'Lead time' → need investigation
#   - 'Defect rates' is a decimal (e.g. 0.22 = 22%) — we'll keep raw and add a % column
#   - 'Costs' and 'Shipping costs' are separate → 'Costs' = manufacturing/ops cost


# =============================================================================
# SECTION 2 — CLEAN COLUMN NAMES
# Goal: Standardise all column names to snake_case (lowercase, underscores).
#       This is required before loading into PostgreSQL — SQL doesn't like spaces.
# =============================================================================

# Before
print("\nBefore rename:", df.columns.tolist())

df.columns = (
    df.columns
    .str.strip()                        # remove leading/trailing spaces
    .str.lower()                        # all lowercase: 'Product type' → 'product type'
    .str.replace(' ', '_', regex=False) # spaces → underscores: 'product type' → 'product_type'
    .str.replace(r'[^\w]', '', regex=True)  # remove any special characters
)

# After
print("\nAfter rename:", df.columns.tolist())

# WHAT YOU'LL SEE:
# 'Number of products sold' → 'number_of_products_sold'
# 'Revenue generated'       → 'revenue_generated'
# 'Lead times'              → 'lead_times'
# 'Lead time'               → 'lead_time'   (← different column! we'll handle this)


# =============================================================================
# SECTION 3 — INVESTIGATE THE DUPLICATE LEAD TIME COLUMNS
# 'lead_times'  = days from order placement to shipment dispatch (supply chain)
# 'lead_time'   = manufacturing lead time for production (operations)
# They are DIFFERENT metrics — we keep both but rename for clarity.
# =============================================================================

print("\n Lead times vs Lead time sample:")
print(df[['sku', 'lead_times', 'lead_time', 'manufacturing_lead_time']].head(10))

# Rename to make intent crystal clear
df = df.rename(columns={
    'lead_times':               'supply_lead_time_days',   # order → dispatch
    'lead_time':                'supplier_lead_time_days', # supplier-quoted days
    'number_of_products_sold':  'units_sold',              # shorter, cleaner
    'manufacturing_lead_time':  'mfg_lead_time_days',      # manufacturing
})

print("\n Columns renamed for clarity")


# =============================================================================
# SECTION 4 — DATA TYPE VALIDATION & FIXES
# Goal: Make sure every column has the right type.
#       Wrong types cause silent errors in SQL and Power BI calculations.
# =============================================================================

# Check numeric columns for any hidden string values
numeric_cols = [
    'price', 'availability', 'units_sold', 'revenue_generated',
    'stock_levels', 'supply_lead_time_days', 'order_quantities',
    'shipping_times', 'shipping_costs', 'supplier_lead_time_days',
    'production_volumes', 'mfg_lead_time_days', 'manufacturing_costs',
    'defect_rates', 'costs'
]

for col in numeric_cols:
    # pd.to_numeric with errors='coerce' → turns bad values into NaN instead of crashing
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Check if coercion created any new nulls (it would mean hidden bad data existed)
new_nulls = df[numeric_cols].isnull().sum()
print("\n Nulls after type coercion (should all be 0):")
print(new_nulls[new_nulls > 0] if new_nulls.sum() > 0 else " No new nulls — data is clean")

# Round financial columns to 2 decimal places (cents precision)
df['price']                = df['price'].round(2)
df['revenue_generated']    = df['revenue_generated'].round(2)
df['manufacturing_costs']  = df['manufacturing_costs'].round(2)
df['shipping_costs']       = df['shipping_costs'].round(2)
df['costs']                = df['costs'].round(2)

print("\n Numeric types validated and financials rounded to 2dp")


# =============================================================================
# SECTION 5 — CATEGORICAL COLUMN STANDARDISATION
# Goal: Fix inconsistent casing/spacing in text columns.
#       'haircare' vs 'Haircare' vs 'HAIRCARE' would become 3 separate groups in Power BI.
# =============================================================================

cat_cols = [
    'product_type', 'customer_demographics', 'shipping_carriers',
    'supplier_name', 'location', 'inspection_results',
    'transportation_modes', 'routes'
]

for col in cat_cols:
    df[col] = df[col].str.strip().str.title()
    # .strip()  → removes hidden spaces
    # .title()  → 'haircare' → 'Haircare', 'non-binary' → 'Non-Binary'

# Verify unique values look clean
print("\n Categorical columns standardised. Unique values:")
for col in cat_cols:
    print(f"  {col}: {sorted(df[col].unique())}")


# =============================================================================
# SECTION 6 — FEATURE ENGINEERING
# Goal: Create NEW columns from existing ones that add business value.
#       These become your most impactful Power BI measures and KPIs.
# =============================================================================

# ── 6a. PROFIT MARGIN ─────────────────────────────────────────────────────────
# Formula: (Revenue - Cost) / Revenue
# Tells us: how much of every £1 of revenue is actual profit
# np.where handles the edge case where revenue = 0 (avoid division by zero)

df['profit_margin_pct'] = np.where(
    df['revenue_generated'] > 0,
    ((df['revenue_generated'] - df['costs']) / df['revenue_generated'] * 100).round(2),
    0
)

print("\n Profit Margin % sample:")
print(df[['sku', 'revenue_generated', 'costs', 'profit_margin_pct']].head(5))


# ── 6b. ON-TIME DELIVERY FLAG ─────────────────────────────────────────────────
# Logic: If actual shipping_time <= supply_lead_time, it was on time
# np.where is like Excel's IF: np.where(condition, value_if_true, value_if_false)
# Result: 1 = on time, 0 = delayed

df['on_time_flag'] = np.where(
    df['shipping_times'] <= df['supply_lead_time_days'], 1, 0
)

# On-Time Delivery Rate (as %)
otd_rate = df['on_time_flag'].mean() * 100
print(f"\n Overall On-Time Delivery Rate: {otd_rate:.1f}%")


# ── 6c. DELAY DAYS ────────────────────────────────────────────────────────────
# How many days PAST the lead time did it arrive?
# .clip(lower=0) → negative values (early deliveries) become 0, not negative

df['delay_days'] = (df['shipping_times'] - df['supply_lead_time_days']).clip(lower=0)

print("\n Delay days distribution:")
print(df['delay_days'].describe().round(2))


# ── 6d. DEFECT RISK TIER ──────────────────────────────────────────────────────
# Bin continuous defect_rates into 3 business-friendly categories
# pd.cut → splits a numeric column into labeled buckets (like binning in Excel)
# bins   → the boundary values: 0–2% = Low, 2–3.5% = Medium, 3.5–5% = High

df['defect_risk_tier'] = pd.cut(
    df['defect_rates'],
    bins=[0, 2.0, 3.5, 5.0],
    labels=['Low', 'Medium', 'High'],
    include_lowest=True
)

print("\n Defect Risk Tier distribution:")
print(df['defect_risk_tier'].value_counts())


# ── 6e. REVENUE PER UNIT ──────────────────────────────────────────────────────
# Average revenue earned per unit sold — proxy for pricing efficiency

df['revenue_per_unit'] = np.where(
    df['units_sold'] > 0,
    (df['revenue_generated'] / df['units_sold']).round(2),
    0
)


# ── 6f. STOCK HEALTH STATUS ───────────────────────────────────────────────────
# Compare current stock to order quantities to flag potential stockouts
# If stock < 25% of typical order quantity → "Critical"

df['stock_health'] = pd.cut(
    df['stock_levels'],
    bins=[0, 20, 50, 100],
    labels=['Critical', 'Watch', 'Healthy'],
    include_lowest=True
)

print("\n Stock Health distribution:")
print(df['stock_health'].value_counts())


# ── 6g. COST EFFICIENCY RATIO ─────────────────────────────────────────────────
# Total cost (manufacturing + shipping) as % of revenue
# Lower = better. >100% means losing money on that SKU.

df['total_cost'] = df['costs'] + df['shipping_costs']
df['cost_efficiency_pct'] = np.where(
    df['revenue_generated'] > 0,
    (df['total_cost'] / df['revenue_generated'] * 100).round(2),
    0
)


# =============================================================================
# SECTION 7 — QUICK EDA VISUALISATIONS
# Goal: Spot patterns and anomalies visually. Save as images for your README.
# =============================================================================

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Supply Chain EDA — Key Distributions', fontsize=16, fontweight='bold')

# Plot 1: Revenue by Product Type
df.groupby('product_type')['revenue_generated'].sum().sort_values().plot(
    kind='barh', ax=axes[0, 0], color='steelblue', edgecolor='white')
axes[0, 0].set_title('Total Revenue by Product Type')
axes[0, 0].set_xlabel('Revenue ($)')

# Plot 2: Defect Risk Tier distribution
df['defect_risk_tier'].value_counts().plot(
    kind='bar', ax=axes[0, 1],
    color=['#2ecc71', '#f39c12', '#e74c3c'], edgecolor='white')
axes[0, 1].set_title('Defect Risk Tier Count')
axes[0, 1].set_xlabel('')
axes[0, 1].tick_params(axis='x', rotation=0)

# Plot 3: On-Time vs Delayed
pd.Series({'On Time': df['on_time_flag'].sum(),
           'Delayed': (df['on_time_flag'] == 0).sum()}).plot(
    kind='pie', ax=axes[0, 2],
    colors=['#2ecc71', '#e74c3c'],
    autopct='%1.1f%%', startangle=90)
axes[0, 2].set_title('On-Time Delivery Split')
axes[0, 2].set_ylabel('')

# Plot 4: Profit Margin distribution
axes[1, 0].hist(df['profit_margin_pct'], bins=15, color='mediumslateblue', edgecolor='white')
axes[1, 0].set_title('Profit Margin % Distribution')
axes[1, 0].set_xlabel('Margin %')

# Plot 5: Shipping cost by transport mode
df.groupby('transportation_modes')['shipping_costs'].mean().sort_values().plot(
    kind='bar', ax=axes[1, 1], color='darkorange', edgecolor='white')
axes[1, 1].set_title('Avg Shipping Cost by Transport Mode')
axes[1, 1].tick_params(axis='x', rotation=30)

# Plot 6: Delay days by supplier
df.groupby('supplier_name')['delay_days'].mean().sort_values(ascending=False).plot(
    kind='bar', ax=axes[1, 2], color='tomato', edgecolor='white')
axes[1, 2].set_title('Avg Delay Days by Supplier')
axes[1, 2].tick_params(axis='x', rotation=30)

plt.tight_layout()
plt.savefig('../assets/screenshots/eda_overview.png', dpi=150, bbox_inches='tight')
plt.show()
print("\n EDA chart saved to assets/screenshots/")


# =============================================================================
# SECTION 8 — FINAL COLUMN REVIEW & EXPORT
# Goal: Confirm the final cleaned dataframe and export to CSV for SQL loading.
# =============================================================================

print("\n Final column list:")
for col in df.columns:
    print(f"  {col:35s} → {str(df[col].dtype)}")

print(f"\n Final shape: {df.shape}")

# Reorder columns logically: identifiers → product → supplier → shipping → metrics → engineered
final_cols = [
    # Identifiers
    'sku', 'product_type',
    # Product
    'price', 'availability', 'units_sold', 'revenue_generated',
    'stock_levels', 'stock_health', 'order_quantities',
    # Customer
    'customer_demographics',
    # Supplier
    'supplier_name', 'location',
    'supplier_lead_time_days', 'supply_lead_time_days',
    'production_volumes', 'mfg_lead_time_days', 'manufacturing_costs',
    'inspection_results', 'defect_rates', 'defect_risk_tier',
    # Shipping
    'shipping_carriers', 'transportation_modes', 'routes',
    'shipping_times', 'shipping_costs',
    # Financials
    'costs', 'total_cost',
    # Engineered KPI columns
    'profit_margin_pct', 'on_time_flag', 'delay_days',
    'revenue_per_unit', 'cost_efficiency_pct'
]

df_final = df[final_cols]

# Export
df_final.to_csv('../data/processed/supply_chain_clean.csv', index=False)
print("\n Cleaned dataset exported → data/processed/supply_chain_clean.csv")
print(f"   Rows: {df_final.shape[0]} | Columns: {df_final.shape[1]}")

# Quick sanity check on engineered columns
print("\n Sample of engineered columns:")
print(df_final[['sku', 'profit_margin_pct', 'on_time_flag',
                'delay_days', 'defect_risk_tier', 'stock_health']].head(8).to_string())
