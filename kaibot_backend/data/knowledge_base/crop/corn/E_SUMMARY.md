# Batch 33 Source E — Summary

**Source PDF**: 46-page GDA/MAFF document "ផលិតកម្មដំណំពោតផ្អែម" (Sweet Corn Production Handbook), produced under the Agriculture Development and Economic Growth Project in partnership with SNV, compiled by staff of the Rice Crop Department and Extension Department of the General Directorate of Agriculture. PDF metadata shows creation date 2017.

**Confirmed subject**: This document is genuinely about **corn (ពោត / sweet corn ពោតផ្អែម)**, not rice. The author affiliation (Rice Crop Department) is just their home department — the entire body content (46 pages) is corn botany, growth stages, agronomy, pest/disease management, and harvest. OCR/text-layer renders ពោត (corn) as "រោត" in several places due to font substitution — this was cross-checked visually against page images and confirmed to be ពោត (corn) throughout, including explicit "Corn Borer," "Corn Flea Beetle" English pest names in section headers.

**Files produced**: 15 JSON files, all prefixed `E_`.

1. `E_corn_intro_uses.json` — introduction, history in Cambodia, nutritional composition, food/industrial/research uses (plan)
2. `E_corn_morphology.json` — plant parts, root types, ear/husk photos, pollination diagram (grow)
3. `E_corn_growth_stages_vegetative.json` — germination through stem elongation stages 1-3 (grow)
4. `E_corn_growth_stages_reproductive.json` — flowering through maturity, stages 4-8 (grow)
5. `E_corn_environmental_requirements.json` — soil pH, moisture, temperature, light, wind, water needs (grow)
6. `E_corn_planting_season_seed_selection.json` — rainy/dry season planting windows, seed quality criteria, germination testing method (plant)
7. `E_corn_land_preparation.json` — plowing/fallow practices by season, bed formation (land_prep)
8. `E_corn_planting_method_spacing.json` — seed treatment, planting depth, spacing table (verified against image) (plant)
9. `E_corn_fertilization.json` — organic and NPK fertilizer schedule/rates table (verified against image) (grow)
10. `E_corn_weeding_irrigation.json` — weeding/hilling schedule, irrigation timing (grow)
11. `E_corn_diseases.json` — 5 diseases (leaf blight, stalk rot, banded leaf/sheath blight, seed rot, seedling blight) with symptoms/control (grow)
12. `E_corn_pests.json` — 5 insect pests (black cutworm, armyworm, corn earworm, corn borer, corn flea beetle) with symptoms/control (verified against image) (grow)
13. `E_corn_harvest.json` — harvest timing, post-harvest cooling/packing/transport (harvest)
14. `E_corn_nutrient_deficiency_diagnosis.json` — Appendix 7 visual nutrient-deficiency diagnostic key (N, P, K, Mg, S, Mo, Fe, and others), verified against multiple page images (grow)
15. `E_corn_seed_companies_and_market_price_reference.json` — Appendix 4-5 seed company/variety list and historical Phnom Penh retail seed prices, flagged as time-specific/possibly outdated (sell)

(Count note: 15 topic files listed above, all written to output directory.)

## Visual spot-checks performed
Rendered and read as images: pages corresponding to printed pages 6-7, 13-15, 20 (spacing table), 22 (fertilizer table), and printed pages 25-38 (pest/disease sections and full nutrient-deficiency appendix, printed pages 32-38). All cross-checked tables (planting spacing, fertilizer rates) matched the `pdftotext -layout` extraction exactly — no numeric discrepancies were found between the text layer and the rendered images for these tables.

## Skipped / flagged as uncertain
- Appendix 1-3 (cost/income/profit analysis tables, printed pages 29-30) were confirmed via text as **empty template forms** with no actual filled-in data — nothing to extract.
- Appendix 6 (disease/pest symptom-vs-growth-stage cross-reference table, printed pages 32-34): this is a dense diagnostic grid missed entirely by `pdftotext` (page came back blank in the text layer) and recovered only via image inspection. Several individual cells were too terse/ambiguous in the source Khmer to translate reliably; these were explicitly omitted rather than guessed, and this is noted inline in `E_corn_nutrient_deficiency_diagnosis.json`.
- Appendix 7 nutrient-deficiency diagram (printed pages 35-38): translated the general diagnostic logic and several detailed nutrient write-ups (P, K, S, Mo, Mg, Fe) with reasonable confidence; a couple of specific nutrient labels in the branching chart (notably the exact identity of one "Potassium" branch label) were harder to read with full confidence from the scan and are flagged inline in the JSON as uncertain rather than stated as fact.
- No numeric discrepancies were found between diagram/table labels and body text for the growth-stage day-counts or fertilizer/spacing tables — all cross-checked figures were consistent.
