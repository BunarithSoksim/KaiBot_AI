# Batch 33 Summary — Files F & G (Corn / ពោត)

## File F — "11_Corn_manual_body+covers" (TSTD, TA 7305-CAM, May 2012), 12 pages
**Text layer status: confirmed unusable (legacy Limon font, garbled).** All 12 pages were rendered to PNG at 150dpi and read visually. **The rendered images were fully legible** — the Limon-font issue only affects the invisible text layer, not the printed appearance, so no content had to be skipped as illegible. All 12 pages were successfully read.

Produced **8 JSON topic files** (prefix `F_`):
1. `F_program_background.json` — TSTD/ADB/AusAID/East West Seed project context (cover + foreword)
2. `F_land_prep_bedding.json` — land clearing, plowing, bed-making (hand vs. tiller)
3. `F_seed_selection_planting.json` — seed source/purity/germination checks, sowing methods
4. `F_fertilizer_schedule.json` — 5-stage NPK/urea/compost schedule with gram-per-hole rates
5. `F_watering_care.json` — irrigation timing and water-quality caution
6. `F_diseases.json` — leaf blight, Pythium stalk rot, banded leaf & sheath blight
7. `F_pests.json` — cutworm, Asian corn borer
8. `F_harvest.json` — 65-75 day fresh-corn harvest window
9. `F_record_keeping_economics.json` — cost/income record-keeping templates and TVC/TFC/TC formulas

(9 files total — corrected count from initial plan of 8, since program background was split out.)

## File G — "ដំណំពោត" (Corn Crop), 8 pages, working text layer
Extracted via `pdftotext -layout`, then **every page was also rendered to PNG and visually spot-checked** against the extracted text, including the two data tables (fertilizer NPK-by-stage table, planting-spacing table). All numbers matched between text extraction and rendered image — no discrepancies found.

Produced **11 JSON topic files** (prefix `G_`):
1. `G_corn_history_status_cambodia.json` — history since 17th century, French-era imports, Khmer red corn breeding (1930s, Phnom Penh & Kampong Cham)
2. `G_corn_nutrition_and_food_use.json` — proximate composition, food uses, 1996 production (63.5k tons), "#1 crop by 2000" projection
3. `G_corn_industrial_uses.json` — stalk/cob for paper, charcoal, animal feed, glue, medicine, bread/oil/sauce
4. `G_corn_scientific_research_value.json` — corn as a genetics/breeding research model plant
5. `G_corn_botanical_characteristics.json` — life cycle length, plant height, leaf dimensions, monoecious flower structure
6. `G_corn_seed_selection.json` — yield, purity >95%, germination >85%, freshness, resistance criteria
7. `G_corn_planting_season_and_regions.json` — riverside/red-soil provinces, dry/wet season windows
8. `G_corn_land_preparation.json` — dry-season deep plow vs. wet-season shallow/repeated plow-fallow
9. `G_corn_fertilizer_schedule.json` — NPK % by growth stage table + kg/ha rates + placement method
10. `G_corn_planting_method.json` — seed rate (25-30kg/ha), soaking, row/hill spacing table, planting depth
11. `G_corn_care_gapfill_thinning_hilling.json` — replanting failed hills, thinning to 1-2 plants/hill, hilling/weeding frequency
12. `G_corn_harvest.json` — visual maturity signs, <25% kernel moisture at harvest

(12 files total.)

## Discrepancies flagged
None found. All table figures (fertilizer NPK percentages/kg-per-ha, plant spacing/population figures) were cross-checked between the extracted/OCR-read text and the rendered page images for both files, and all matched consistently — no numeric conflicts to report.

## Nothing skipped
No pages from either file were skipped. File F's Limon-font text layer is confirmed garbage/unusable as text, but every page was fully readable as a rendered image, so no content loss occurred.
