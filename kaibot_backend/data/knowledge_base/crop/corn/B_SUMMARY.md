# Batch 33 - Source B Summary

**Source document:** "ដំណំពោត" (Corn Crop / Zea mays production manual), 65-page image-only PDF, published 2015.

**Confirmed province:** Kandal (មន្ទីរកសិកម្មខេត្តកណ្តាល = Kandal Provincial Department of Agriculture). The task brief suggested this might say Battambang, but the cover and header on every interior page clearly read "កណ្តាល" (Kandal), not Battambang.

**Total JSON files produced:** 43 (all prefixed `B_`), covering all 65 pages of the source.

## Topics covered

**General crop knowledge (10 files):** history and global importance, nutritional value/industrial uses, botanical characteristics (roots/stem/leaf/tassel/silk/ear), growth stages (5-stage cycle), nutrient requirements (N/P/K), water requirements, planting seasons, land selection, tillage schedule (2-pass), seed selection, planting method and spacing, fertilizer application schedule, weeding.

**Diseases (16 files):** seed rot, seedling blight, root rot, leaf spot (ព្រុកចាប), corn smut (Ustilago), nematode, rust/gray leaf spot, anthracnose, charcoal rot (Macrophomina), Fusarium wilt, stem blotch, Gibberella ear/stalk rot, Fusarium kernel rot, general virus overview, Maize dwarf mosaic virus, planthopper-transmitted mosaic virus, sugarcane mosaic virus.

**Insect pests (9 files):** seed corn maggot, aphids (melon aphid + corn leaf aphid + natural enemies), fall armyworm (Spodoptera frugiperda), corn earworm/fruit borer (Helicoverpa zea), corn stalk borer (Diatraea lineolata), cucumber beetle/rootworm (Diabrotica spp), corn flea beetle, thrips, white grub (Phyllophaga spp).

**Harvest/post-harvest (4 files):** harvest maturity indicators, harvest method (hand harvest in Cambodia), drying methods (machine vs. sun drying), seed storage.

## Pages skipped as illegible
None wholesale-skipped. One growth-stage sub-section ("Stage 4 - ear/grain development period", ពេលលូតលាស់ផ្លែ) is named in the source but its detailed paragraph was not clearly legible/located in the scanned pages, so that stage's description was left out of `B_corn_growth_stages.json` rather than guessed. Pages 1-6 (cover, table of contents, foreword) and page 65 (blank green back cover) contained no substantive agronomic content and were not converted to topic files.

## Numeric discrepancies flagged
1. **Seed germination rate** (`B_corn_seed_selection.json`): source text reads "85 to 900%" for germination rate — a printing/OCR error since germination cannot exceed 100%; likely intended ~90%, reported as-is rather than silently corrected.
2. **Nitrogen top-dress split arithmetic** (`B_corn_fertilizer_application.json`): source states basal N = 5%, then two top-dressings of 25% each are said to cover the "remaining 95%" — but 5%+25%+25% = 55%, not 100%. This ~45% gap in the source's own numbers is reported rather than resolved by guessing (possible missing third top-dressing not legible in the scan).
3. Two NPK compound-fertilizer application rates are given for different plant stages (200 kg/ha at 6-8 leaves vs. 190 kg/ha at 10-12 leaves) — these are preserved as distinct figures per growth stage, not treated as a conflict.

No conflicting diagram-vs-text numeric pairs were found on spacing/fertilizer figures beyond the above; where a table/diagram was present alongside body text (e.g. planting spacing, tillage depths), the two matched.
