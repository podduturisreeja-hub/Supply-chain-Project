-- VIEW 1: SUPPLIER PERFORMANCE SCORECARD
-- Business Question: Which suppliers are reliable and which are risky?

SELECT
    s.supplier_name,
    s.location,
    COUNT(*)                                         AS total_orders,
    ROUND(AVG(f.on_time_flag) * 100, 1)             AS otd_rate_pct,
    ROUND(AVG(f.delay_days), 1)                      AS avg_delay_days,
    ROUND(AVG(f.defect_rates), 4)                    AS avg_defect_rate,
    ROUND(SUM(f.revenue_generated), 2)               AS total_revenue,
    ROUND(AVG(f.profit_margin_pct), 2)               AS avg_profit_margin,
    CASE
        WHEN AVG(f.on_time_flag) * 100 >= 85 THEN 'Low Risk'
        WHEN AVG(f.on_time_flag) * 100 >= 70 THEN 'Medium Risk'
        ELSE 'High Risk'
    END                                              AS supplier_risk_tier
FROM fact_supply_chain f
JOIN dim_supplier s ON f.supplier_key = s.supplier_key
GROUP BY s.supplier_name, s.location
ORDER BY otd_rate_pct DESC;


-- VIEW 2: PRODUCT PROFITABILITY ANALYSIS
-- Business Question: Which products and SKUs drive the most profit?

SELECT
    p.product_type,
    p.sku,
    p.price,
    SUM(f.units_sold)                                AS total_units_sold,
    ROUND(SUM(f.revenue_generated), 2)               AS total_revenue,
    ROUND(SUM(f.costs), 2)                           AS total_cost,
    ROUND(SUM(f.revenue_generated) - SUM(f.costs), 2) AS gross_profit,
    ROUND(AVG(f.profit_margin_pct), 2)               AS avg_profit_margin_pct,
    ROUND(AVG(f.stock_levels), 0)                    AS avg_stock_level,
    ROUND(AVG(f.cost_efficiency_pct), 2)             AS avg_cost_efficiency_pct
FROM fact_supply_chain f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_type, p.sku, p.price
ORDER BY gross_profit DESC;


-- VIEW 3: SHIPPING EFFICIENCY ANALYSIS
-- Business Question: Which transport modes and carriers are fastest and cheapest?

SELECT
    sh.transportation_modes,
    sh.shipping_carriers,
    sh.routes,
    COUNT(*)                                         AS total_shipments,
    ROUND(AVG(f.shipping_times), 1)                  AS avg_shipping_days,
    ROUND(AVG(f.on_time_flag) * 100, 1)             AS otd_rate_pct,
    ROUND(AVG(f.delay_days), 1)                      AS avg_delay_days,
    ROUND(SUM(f.shipping_costs), 2)                  AS total_shipping_cost,
    ROUND(AVG(f.shipping_costs), 2)                  AS avg_shipping_cost,
    CASE
        WHEN AVG(f.shipping_times) <= 3 THEN 'Fast'
        WHEN AVG(f.shipping_times) <= 6 THEN 'Standard'
        ELSE 'Slow'
    END                                              AS speed_tier
FROM fact_supply_chain f
JOIN dim_shipping sh ON f.shipping_key = sh.shipping_key
GROUP BY sh.transportation_modes, sh.shipping_carriers, sh.routes
ORDER BY otd_rate_pct DESC;


-- VIEW 4: DEFECT & QUALITY RISK SUMMARY
-- Business Question: Where are quality problems concentrated?

WITH quality_base AS (
    SELECT
        p.product_type,
        s.supplier_name,
        i.inspection_results,
        f.defect_rates,
        f.defect_risk_tier,
        f.revenue_generated,
        f.costs
    FROM fact_supply_chain f
    JOIN dim_product    p ON f.product_key    = p.product_key
    JOIN dim_supplier   s ON f.supplier_key   = s.supplier_key
    JOIN dim_inspection i ON f.inspection_key = i.inspection_key
)
SELECT
    product_type,
    supplier_name,
    inspection_results,
    COUNT(*)                                     AS total_records,
    ROUND(AVG(defect_rates), 4)                  AS avg_defect_rate,
    ROUND(MAX(defect_rates), 4)                  AS max_defect_rate,
    SUM(CASE WHEN defect_risk_tier = 'High'
             THEN 1 ELSE 0 END)                  AS high_risk_count,
    ROUND(SUM(revenue_generated), 2)             AS total_revenue,
    ROUND(SUM(costs), 2)                         AS total_cost
FROM quality_base
GROUP BY product_type, supplier_name, inspection_results
ORDER BY avg_defect_rate DESC;
