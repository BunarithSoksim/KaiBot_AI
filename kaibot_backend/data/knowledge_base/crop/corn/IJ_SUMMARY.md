# Batch 33 Extraction Summary (Files I & J)

## File I (Svay Rieng farmer-led corn trial report, PowerPoint-derived PDF, 23 pages)
Produced **2 JSON files**:
- `I_corn_farmer_trial_methodology.json` — background/rationale for the Polinuovo (Robolino) farmer-initiative program, trial objectives, responsible staff, work activities, and the common land-prep/planting/fertilizer method used across trial plots.
- `I_corn_farmer_trial_results.json` — weekly growth data (stalk height/leaf count), harvest results across ~10 participating farmers (individual plot totals roughly 72-90 kg, one outlier farmer "Nut Suong" yielding visibly more per the summary bar charts), and the report's conclusion/recommendation.

Reading order was visually spot-checked against rendered page images (pages 9-12, 20-23) — the PowerPoint text layer's reading order matched the visual layout well for this document; no reordering issues found.

**Numeric discrepancy flagged**: the report's conclusion (page 23) states the top-performing farmer (Nut Suong) used a fertilizer regimen of 0.2 kg base fertilizer and 0.9 kg chemical fertilizer per top-dressing round — but this farmer's own individual results table earlier in the document (pages ~10-11) records base fertilizer of ~0.5 kg and top-dressing chemical-fertilizer amounts of roughly 5, 8, and 11-12 kg per round (with 9-21 kg organic fertilizer per round). Both figures are reported verbatim in `I_corn_farmer_trial_results.json` with the discrepancy explicitly called out; neither was "corrected" or guessed.

**Skipped as illegible**: several individual farmer result tables (pages ~13-19) have blank/missing numeric cells in the source PDF itself (hole spacing, base fertilizer amount, planting date, some week-by-week growth figures) — not reconstructed, and noted as a data-quality caveat in the results JSON rather than omitted silently. Individual farmer names on the small chart axis labels (pages 20-21) were too blurry to transcribe reliably and were not guessed; only the one farmer name stated clearly in body text ("Nut Suong") was used.

## File J (Climate-resilient sweet corn cultivation guide, MAFF/ASPIRE, 2018, 23 pages)
**Determined to be corn-specific and in scope.** Although the document opens with generic framing about climate-change-adaptive agricultural extension in general, its title and entire body (from page 2 onward) are specifically about "ដំណំពោតផ្អែម" (sweet corn) cultivation — variety selection, land preparation, planting (direct seed vs. seedling transplant), watering/fertilizing schedule, pest and disease management, crop rotation, harvest, market calendar, and a business/economic-analysis plan template for corn production. This is a complete corn-specific technical extension manual, not a multi-crop generic guide.

Produced **5 JSON files**:
- `J_corn_variety_selection.json` — uses of corn, seed selection criteria, program/document purpose statement.
- `J_corn_land_prep_and_planting.json` — bed preparation, mulching, direct seeding and seedling-transplant methods.
- `J_corn_care_watering_fertilizing.json` — weeding, watering, and the detailed 5-stage fertilizer schedule (with a flagged unit-jump anomaly, see below).
- `J_corn_pests_and_diseases.json` — 2 insect pests (cutworm, corn borer) and 3 diseases (yellow leaf wilt, stem rot, leaf blight) with symptoms and control measures.
- `J_corn_crop_rotation_and_harvest.json` — rotation crops/benefits, harvest timing and indicators, post-harvest stalk use, market-timing note, and business-plan/economic-analysis table structure.

Text layer for File J was clean, non-scrambled body text (not PowerPoint-derived reading-order issues); reliable to extract directly from `pdftotext -layout` output; spot-checked visually only for illustrative images (which carried no extractable numeric data beyond what's in the fertilizer table already captured in text).

**Numeric discrepancy flagged**: the fertilizer schedule table (page ~9) records the pre-planting 20-20-15 fertilizer application as "5 grams per hill," but the two post-planting applications of the same 20-20-15 formula jump to "5 kg per hill" and "10 kg per hill" respectively — a roughly 1000x unit jump that may be a genuine large increase in application rate as the plant matures, or may reflect a gram/kilogram inconsistency in the original document. Reported verbatim in `J_corn_care_watering_fertilizing.json` with the discrepancy explicitly flagged, not corrected.

**Skipped as illegible**: none for File J — the running body text was legible throughout; only decorative photos (variety photos, tool photos) were not text-extracted since they carried no numeric/factual content beyond captions already covered in the corresponding JSON topic.

## Totals
- File I: 2 JSON topics
- File J: 5 JSON topics (in scope, corn-specific)
- Total: 7 JSON files, all prefixed `I_` or `J_`, all validated as parseable JSON.
