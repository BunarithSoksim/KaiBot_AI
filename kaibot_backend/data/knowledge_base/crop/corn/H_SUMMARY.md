# Batch 33 — Source H Summary

**Source document:** "TIP Training on Maize Production" / បទដ្ឋានអនុវត្ដបច្ចេកវិទ្យា ផលិតកម្មដំណំពូតក្របម — CARE Cambodia (Pailin program), 2009. Funded by AusAID (ACIMA project), the European Union (Pailin Food Security Program / PFSP), and ACIAR (CCPMP project). 29-page PDF with text layer, three-stage extension training structure (land prep/planting → weed & nutrient management → harvest/post-harvest).

**JSON files produced:** 18, all under `/tmp/kasekor_batch33/output/`, all prefixed `H_`, all validated as parseable JSON.

**Topics covered:**
1. `H_corn_site_selection.json` — land_prep
2. `H_corn_land_preparation.json` — land_prep (ploughing purpose/timing, residue burning trade-offs)
3. `H_corn_seed_variety_selection.json` — plan (hybrid seed caveat, Pioneer 30K95 / CP888 / Pioneer 30B80)
4. `H_corn_preplant_weed_management.json` — land_prep (timing ploughing vs. weed germination)
5. `H_corn_herbicide_glyphosate.json` — land_prep
6. `H_corn_herbicide_paraquat.json` — land_prep
7. `H_corn_herbicide_atrazine.json` — land_prep
8. `H_corn_herbicide_24d.json` — land_prep
9. `H_corn_pesticide_safety.json` — land_prep (poisoning symptoms, PPE, environmental fate)
10. `H_corn_planting_spacing.json` — plant
11. `H_corn_basal_fertilizer.json` — plant (DAP)
12. `H_corn_nutrient_nitrogen.json` — grow
13. `H_corn_nutrient_phosphorus.json` — grow
14. `H_corn_nutrient_potassium.json` — grow
15. `H_corn_topdressing_method.json` — grow
16. `H_corn_harvesting.json` — harvest
17. `H_corn_drying_storage.json` — process
18. `H_corn_general_recommendations.json` — plan (cross-cutting summary)

**Method:** Extracted with `pdftotext -layout`, then rendered all 29 pages to PNG at 150dpi and visually cross-checked every page containing a table, spacing diagram, herbicide product photo, or numeric figures (pages 1, 12-15, 17, 22, 24, 27 specifically inspected in detail).

**Numeric discrepancy flagged (confirmed by visual inspection of two separate pages, not a transcription error):**
- The document states DAP fertilizer's phosphorus content as **46%** in the basal-fertilizer section (Stage 1, "ការប្រើជីប្រាប់បាត") but as **48%** (P2O5) in the plant-nutrition section (Stage 2, phosphorus sub-topic). Both figures were verified directly from page images. This discrepancy is called out explicitly in `H_corn_basal_fertilizer.json` and `H_corn_nutrient_phosphorus.json` rather than silently resolved.

**Spacing/diagram cross-check:** The planting spacing diagram (page 13/14 region) was visually verified against the body text — row spacing 0.7m and both hill-spacing options (0.5m/2 seeds per hole, 0.25m/1 seed per hole) match exactly between diagram and prose. No discrepancy found there.

**Herbicide identification:** Product label photos were used to confirm active ingredients behind the Khmer/local brand names used in the text: "ទឹកខ្មៅ" = glyphosate (label: "ไกลโฟเซต48"/Glyphosate 48%), "ដោខ្វត"/"ទឹកសៀវ" = paraquat (label: "เอราโซน ERAZONE", paraquat dichloride), "អាសាពន" = atrazine (label: "อาทราซีน 80"), and the fourth product = 2,4-D (label shows "2,4-D sodium salt" with a red-dog logo). The local Pailin brand name for the 2,4-D product was not clearly legible in the OCR/scan and was intentionally omitted from `H_corn_herbicide_24d.json` rather than guessed.

**Skipped/illegible content:** A few short OCR artifacts (e.g., "QuickTime™ and a decompressor are needed to see this picture" — an embedded-image placeholder artifact, not real content) were ignored. The organization name "អងគការដែរ" in the front-matter narrative text was garbled in pdftotext output; the cover page image (visually inspected) confirmed the organization is CARE (Pailin office), so the citation uses that verified name rather than the garbled OCR string. No sections were skipped as wholly illegible — the full 29 pages were reviewed either via text extraction or direct page-image inspection.
