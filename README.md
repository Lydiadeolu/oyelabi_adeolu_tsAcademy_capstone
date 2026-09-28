# Enterprise Logistics Intelligence & Executive Dashboard

## Executive Summary

This project transforms a raw Python logistics data pipeline into an enterprise-grade, high-performance **Power BI Executive Dashboard**. By transitioning from pre-aggregated Python tables to a dynamic **Star Schema** model powered by optimized **DAX measures**, this solution provides real-time, multi-dimensional visibility into commercial health, fleet utilization, route profitability, and risk management.

---

## Architecture & Data Model

### 1. Data Pipeline & Schema Design

* **Source-to-Model Transformation:** Refactored a complex 22-table data model by eliminating redundant pre-aggregated summary tables via Power Query (`Enable Load` set to false), enforcing a clean and scalable **Star Schema**.
* **Fact Tables:** Central transactional hubs capturing core operational events (`loads`, `trips`, `delivery_events`, `safety_incidents`, `maintenance_records`, `fuel_purchases`).
* **Dimension Tables:** Descriptive context surrounding business entities (`customers_csv`, `drivers`, `trucks`, `trailers`, `routes`, `facilities`).
* **Governance:** Centralized all custom calculations into a dedicated `_Measures` table.

### 2. Core DAX Measures Implemented

* **Commercial:** `Total Revenue = SUM(loads[revenue])`, `Total Loads = COUNTROWS(loads)`, `Avg Revenue Per Load = DIVIDE([Total Revenue], [Total Loads], 0)`, `On-Time Delivery Rate`.
* **Fleet Operations:** `Total Miles = SUM(trips[total_distance])`, `Revenue Per Mile = DIVIDE([Total Revenue], [Total Miles], 0)`, `Average CPM = DIVIDE(SUM(trips[total_cost]), SUM(trips[total_distance]), 0)`.
* **Financials & Route Profitability:** `Total Cost = SUM(trips[total_cost])`, `Net Profit = [Total Revenue] - [Total Cost]`, `Profit Margin = DIVIDE([Net Profit], [Total Revenue], 0)`.
* **Risk & Maintenance:** `Total Maintenance Cost = SUM(maintenance_records[cost])`, `Total Incidents = COUNTROWS(safety_incidents)`, `Maintenance Cost Per Mile = DIVIDE([Total Maintenance Cost], [Total Miles], 0)`.

---


## Dashboard UX/UI Architecture (5-Page Structure)

1. **Page 1: Executive Summary**
* *Focus:* High-level performance scorecards, top-line revenue metrics, and overarching operational summaries designed for C-suite stakeholders.


2. **Page 2: Fleet Utilization**
* *Focus:* Total mileage tracking, asset output ratios, and truck-by-truck operational deployment to identify idle versus high-performing assets.


3. **Page 3: Drivers Performance**
* *Focus:* Individual driver productivity rankings (`Revenue Per Mile`), personal mileage contributions, and individual on-time delivery rates.


4. **Page 4: Financial and Routes Profitability**
* *Focus:* Lane-by-lane financial breakdown comparing operational trip revenues against direct costs, net margins, and fuel efficiency trends.


5. **Page 5: Safety and Maintenance Analysis**
* *Focus:* Asset maintenance overhead (cost per mile), lemon vehicle tracking, repair expenditure spikes, and quarterly safety incident trends.

---

## Analytical Report & Executive Insights

### 1. Commercial Health & Customer Concentration

* **Revenue Scale:** The model tracks over **$262M in Total Revenue**, highlighting a robust enterprise throughput.
* **Customer Concentration Risk:** Analysis on Page 1 reveals that top-tier enterprise clients drive a significant majority of total bookings. However, SLA matrices show strong compliance, with core delivery fulfillment holding near benchmark thresholds. Leadership should monitor tier-one accounts closely to mitigate dependency risks.

### 2. Operational Efficiency & Asset Performance

* **Revenue Per Mile (RPM) Dynamics:** By cross-referencing `[Total Revenue]` with `[Total Miles]`, the fleet analysis highlights high-performing shipping lanes. Drivers with specialized freight routes exhibit significantly higher RPM values compared to regional standard lanes.
* **Cost Management:** Average Cost Per Mile (**CPM** hovering around **$32.29**) acts as a critical baseline guardrail. Lanes where operating costs outpace revenue growth have been isolated on Page 3 for immediate contract renegotiation or route optimization.

### 3. Maintenance Outliers & Safety Compliance

* **Asset Lifecycle Costs:** Tracking `Maintenance Cost Per Mile` on Page 4 successfully flagged high-repair-frequency assets ("lemon trucks"). Immediate capital reallocation toward newer fleet acquisitions will drastically curtail repair budget leakage.
* **Safety Trends:** Incident tracking demonstrates stable quarterly trends, though preventive measures continue to target high-mileage routes to reduce risk exposure.

---

## Getting Started

1. **Prerequisites:** Power BI Desktop installed.
2. **Data Source Configuration:** Point the Power Query data source connections to your localized SQL Server/Data Warehouse containing the core dimensions and fact tables.
3. **Model Refresh:** Open `Transform Data`, verify that pre-aggregated summary tables have load disabled, and click **Close & Apply**.
4. **Explore:** Navigate through the 4 core pages using the established bookmark/navigation structure to begin real-time analytical slicing.

---

*Developed as an enterprise-grade BI template for scalable logistics and supply chain operations.*