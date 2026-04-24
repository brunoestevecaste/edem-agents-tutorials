# Sample Outputs

## RAG-only
- **Answer**: Based on retrieved documents, revenue recognition requires signed contracts and delivery acceptance.
- **Sources Used**: policy_handbook.md

## Talk-with-Data-only
- **Answer**: Regional sales summary with totals by region.
- **Sources Used**: BigQuery structured data
- **SQL**: `SELECT region, SUM(total_sales) ...`

## Hybrid
- **Answer**: EMEA sales are below threshold and therefore not compliant.
- **Sources Used**: regional_thresholds.md + sales_by_region
