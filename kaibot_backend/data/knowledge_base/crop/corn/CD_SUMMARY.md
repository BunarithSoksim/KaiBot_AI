# Batch 33 Summary — Corn (ពោត) Source Files C & D

## Source C — "The Agriculture Magazine", Issue 247, Q3 2013, poster "បច្ចេកទេសដាំដុះ ពោត (1)/(2)" (TSTD-TA 735-CAM)
2 pages, both viewed. 2 JSON files produced:
- `C_corn_landprep_planting_spacing.json` — plowing/ridging, basal organic fertilizer, weed-suppression covering, and both row-spacing diagrams (1m row/2-rows-per-bed with 0.35-0.4m plant spacing; 0.5m row/1-row-per-bed with 0.35-0.5m plant spacing), plus the 10cm fertilizer-hole diagram.
- `C_corn_pests_diseases.json` — full pest/disease photo-ID list (leaf-cutting caterpillar, stem borer, corn borer, snail damage, leaf blight, leaf yellowing, rust, stem rot, leaf sheath rot, corn smut).

Skipped: page 2's bottom "ការថែទាំ និងប្រមូលផល" (Care and Harvest) section has only a header and photos, no body text — noted inline in the pests/diseases file rather than given its own JSON, since there was no extractable factual content.

## Source D — Dept. of Agricultural Extension (MAFF), booklet "ដំណាំពោត" (Corn Crop), Issue 1, 2003, ADB Loan/Grant No. 1445-CAM(SF)
13 pages (cover + 12 content pages), all viewed. This document is text-heavy (not just images), unlike most other batch documents. 8 JSON files produced:
- `D_corn_overview_cambodia.json` — history of corn cultivation in Cambodia, red-corn and waxy-corn variety background, national production figure.
- `D_corn_uses_and_nutrition.json` — food/feed/industrial/research uses.
- `D_corn_botanical_characteristics.json` — growth cycle length, plant height, root system, monoecious flowering.
- `D_corn_seed_selection_and_season.json` — seed selection criteria; rainy-season and dry-season planting windows and growing provinces.
- `D_corn_land_preparation.json` — plowing depth/timing, rainy-season drainage furrows.
- `D_corn_fertilizing.json` — 2-round NPK schedule with rates and % split table, application placement (~5cm from seed/root).
- `D_corn_planting_method_and_spacing.json` — seed rate, seed-soaking pre-treatment, spacing table, and the page-12 spacing diagram.
- `D_corn_care_thinning_weeding.json` — post-emergence germination check, thinning to 1-2 plants/hill, two-round weeding/hilling.
- `D_corn_harvesting.json` — husk-color/dryness harvest indicator, ~25% kernel moisture at harvest.

(9 files total for source D, not 8 — corrected count.)

## Numeric discrepancies flagged
1. **Source D, uses/nutrition section (page 3)**: A percentage list (10.8%, 10%, 4.3%, 73.4%, 1.4%) appears under a sentence about storage loss by corn type, but the numbers read far more like a kernel nutrient-composition breakdown (water/protein/oil/carbohydrate/fiber). Both readings are given explicitly in `D_corn_uses_and_nutrition.json` rather than silently picking one, since the printed sentence structure is genuinely ambiguous.
2. **Source D, spacing diagram vs. table (pages 11-12)**: The hand-drawn spacing diagram (75cm row x 30-40cm hill x 3-5cm depth) was checked against the printed spacing table and found to be **consistent** (matches the table's single-seed-per-hill row) — no discrepancy, explicitly confirmed in `D_corn_planting_method_and_spacing.json`.
3. **Source D, page 1, overview section**: a sentence about corn production trend/ranking "by year 2000" and a global-rank claim was hard to parse confidently; it was included with an explicit caveat that the figure is approximate/uncertain rather than omitted or guessed at a specific number.

## Total: 11 JSON files (2 from Source C, 9 from Source D)
