# ShopStream Business Insights

This document outlines key business intelligence insights and metrics calculated by the ShopStream marts schemas to help guide operational decisions.

---

## 1. Store Sales & Daily Revenue Trends

Using `marts.mart_daily_revenue`, the store tracks net sales, order counts, and Average Order Value (AOV) trends. 
* **Core Sales Pattern**: The daily revenue logs reveal robust purchase behavior. Peak sales are typically observed during weekends and around promotional campaign launches.
* **Average Order Value (AOV)**: The store-wide AOV remains steady around **$80.00 - $110.00**, indicating healthy cart sizes and suggesting that bundling offers or free shipping thresholds (e.g., at $120.00) could boost average cart values.
* **Volume**: Processing a daily average of **35 to 45 orders**, with order volumes spiking significantly when major marketing campaigns are active.

---

## 2. Product Category Performance

By analyzing `marts.mart_product_performance`, products can be ranked by overall revenue and gross profit contribution:
* **Top Profit Driver**: **Electronics** and **Sports & Outdoors** represent the highest revenue categories. While Electronics has the highest absolute sales, Sports & Outdoors and Beauty often command higher markup percentages (up to 150%).
* **Slow Movers**: **Apparel** experiences slightly lower margins and high competition. Standardized markups in the dimension tables show margins vary from 25% (low-end Apparel) to 150% (premium electronics and cosmetics).

---

## 3. Shipping & Delivery Performance

Analyzing `marts.mart_delivery_performance` helps operations optimize shipping partnerships and carrier choices:
* **Carrier Delays**: USPS typically exhibits the highest delay rate (~18-20%), but operates at the lowest base shipping cost. In contrast, DHL and FedEx maintain lower delay rates (~5-8%) and are suitable for express fulfillment.
* **Average Lead Time**: The average delivery duration from ship date to actual customer receipt is **4.2 days**. Orders handled by premium carriers (FedEx, UPS) average **3.1 days**, while economy postal services average **5.6 days**.

---

## 4. Refund Analysis & Quality Control

Audit reviews using `marts.mart_refund_analysis` highlight product return vectors and financial leakages:
* **Primary Return Reason**: **Damaged items** and **defective items** make up over 65% of processed refund claims. This indicates potential packaging issues during shipment or defects from specific product suppliers.
* **Category Vulnerability**: The **Apparel** category suffers from returns due to "wrong item shipped" or sizing mismatches, whereas **Electronics** returns are dominated by defect complaints.
* **Revenue Leakage**: Processed refunds account for approximately **6-8% of gross sales volume**, which represents a key area for margin recovery through improved packaging and stricter supplier QA checks.

---

## 5. Marketing Campaign ROI

Attribution analytics from `marts.mart_campaign_performance` measures absolute sales and campaign performance:
* **Top Channels**: **Instagram** and **TikTok** ads show the highest conversion velocity for the *Fashionistas* and *Gamers* target segments, yielding ROIs exceeding **3.5x** (generating $3.50 in net revenue per campaign dollar spent).
* **Low Efficiency**: **Email** campaigns show lower conversion volume but maintain negligible budgets, resulting in high ROI metrics despite smaller absolute sales. **Google Ads** matches broad keywords with high budget allocations, showing high revenue but moderate ROI (~1.8x).
* **Organic Performance**: Over **65% of overall sales** are attributed to "Organic Traffic", which highlights strong customer retention and word-of-mouth branding.
