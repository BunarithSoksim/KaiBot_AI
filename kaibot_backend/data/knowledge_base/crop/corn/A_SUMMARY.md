# Batch 33 Source A — Corn Production Value Chain in Cambodia (2017) — Extraction Summary

**Source PDF:** 61-page image-only PDF, "ខែ្សសង្វាក់ផលិតកម្ម ដំណាំពោតនៅកម្ពុជា" (Corn Production Value Chain in Cambodia), General Directorate of Agriculture / Boosting Food Production Program (PMO), Royal Government of Cambodia, 2017. A value-chain study covering 250 surveyed red-corn (ដំណាំពោតក្រហម) farming households in Kampong Cham, Kandal, Battambang, and Pailin provinces.

**Pages actually viewed:** All content pages 1-43 (executive summary, TOC, botany, global/national market background, methodology, survey findings, cost/price/profitability tables, value-chain diagrams, constraints, and discussion). Pages 44-61 were confirmed as reference list and a blank survey questionnaire annex (repeated form fields, no new factual content) plus the back cover — no extraction needed from these.

**Output:** 21 JSON files produced, all validated as parseable JSON, prefixed `A_`:

1. corn_plant_botany — plant anatomy/measurements, origin/domestication history (grow)
2. corn_seed_varieties_used — 53 named varieties used by farmers, seed sourcing (plant)
3. corn_variety_selection_reasons — why farmers pick a given seed (plant)
4. corn_national_production_trend — 2007-2016 national output table, yield trend, cultivated area (plan)
5. corn_domestic_demand_and_feedmills — domestic demand table, feed-mill buyers (sell)
6. corn_export_trade — export volumes to Vietnam/Thailand/China, import figures (sell)
7. corn_farmer_demographics — household composition, education, land tenure (plan)
8. corn_growing_stage_timeline — week-by-week soak→germinate→flower→fill→dry timeline (grow)
9. corn_planting_harvest_calendar_by_province — month-by-month planting/harvest windows per province (plant)
10. corn_postharvest_quality_and_mold — drying practices, mold spoilage risk (process)
11. corn_price_wet_vs_dried — price tables by crop round, province, and year (sell)
12. corn_input_cost_structure — full per-hectare cost breakdown (seed/land/fertilizer/labor/etc.) (plan)
13. corn_farm_size_and_landholding — plot sizes, experience, province landholding (grow)
14. corn_yield_revenue_and_profitability — yield, revenue, cost, profit/loss figures (sell)
15. corn_value_chain_actors — 5 categories of input/service suppliers (market)
16. corn_value_chain_flow_kampongcham_kandal — value chain diagram, Vietnam-bound (market)
17. corn_value_chain_flow_battambang_pailin — value chain diagram, Thailand-bound (market)
18. corn_future_challenges_and_expectations — farmer-ranked future risks (grow)
19. corn_value_chain_actor_constraints — constraints by actor type (market)
20. corn_provincial_price_and_mechanization_gaps — Kandal vs Battambang price/seed-use gap discussion (sell)
21. corn_global_and_world_market_context — background global corn production stats (market)

## Skipped as illegible
None of the viewed content pages were illegible — all page text was legible enough to transcribe/summarize honestly. Pages 44-61 (reference list + blank survey questionnaire annex + back cover) were skipped as out-of-scope (no factual agronomic/market content, not "illegible").

## Numeric discrepancies flagged in the JSON `text` fields
- **National corn area/output for 2017**: one passage states cultivated corn area grew to ~113,000 ha producing ~433,000 tons in 2017 (tied to the HLH company's ~10,000 ha contracted area), which is inconsistent in scale with the national totals reported elsewhere in the same document (215,452 ha cultivated in 2013; 748,000 tons national output in 2016). Both figures are reported in `A_corn_cambodia_national_production_trend.json` with the discrepancy explicitly called out, since the source does not reconcile them (likely a company-level vs. national-level scope difference).
- **Pailin dried-kernel price**: the province-level price table shows Pailin's dried-kernel min/max/average all equal to 800 riel/kg, which traces to a sample of essentially one respondent (0.4% of the sample) — flagged as low-confidence in `A_corn_price_wet_vs_dried.json` rather than presented as a reliable provincial average.
- **Profit/loss range**: household-level profitability data includes negative values (as low as -12,300,000 riel/household, -61,100,000 riel/ha) alongside very large positive outliers (66,102,000 riel/household) — reported as-is in `A_corn_yield_revenue_and_profitability.json` with a caution that extreme values at both ends should be treated cautiously rather than as typical outcomes.
