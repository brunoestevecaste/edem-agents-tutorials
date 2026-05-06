# Sample Outputs

## RAG-only
- **Answer**: Based on retrieved documents, revenue is recognized when an order is shipped and payment is captured.
- **Sources Used**: revenue_recognition_policy.md

## Talk-with-Data-only
- **Answer**: Top product categories ranked by revenue from TheLook order items and products.
- **Sources Used**: BigQuery structured data
- **SQL**: `SELECT p.category, SUM(oi.sale_price) AS revenue ...`

## Hybrid
- **Answer**: Categories with return rates above the policy threshold should be reviewed.
- **Sources Used**: refund_policy.md + bigquery-public-data.thelook_ecommerce
