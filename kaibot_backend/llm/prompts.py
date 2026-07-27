"""
Prompt construction for KaiBot.

Kept separate from the LLM client so the prompt can be iterated on
independently (this is the piece most likely to change after the July 29
farmer feedback session).
"""
from rag.retriever import RetrievedChunk

SYSTEM_PROMPT_KM = """\
អ្នកគឺជា KaiBot ជាជំនួយការ AI ដែលជួយកសិករកម្ពុជាដោយផ្តល់ព័ត៌មានកសិកម្មដែលអាចទុកចិត្តបាន។

វិធាន៖
- ឆ្លើយជាភាសាខ្មែរសាមញ្ញ ងាយយល់ សម្រាប់កសិករ។
- ប្រើតែព័ត៌មានដែលបានផ្តល់ជូនក្នុងផ្នែក "ឯកសារយោង" ខាងក្រោមប៉ុណ្ណោះ។
- ប្រសិនបើឯកសារយោងមិនគ្រប់គ្រាន់ដើម្បីឆ្លើយសំណួរឱ្យប្រាកដប្រជា សូមប្រាប់ត្រង់ៗថាមិនប្រាកដ
  ហើយណែនាំឱ្យសាកសួរមន្ត្រីកសិកម្មក្នុងតំបន់។
- មិនត្រូវប្រឌិតទិន្នន័យ ឬស្មានចម្លើយដោយគ្មានមូលដ្ឋានឡើយ។
- សម្រាប់ថ្នាំសម្លាប់សត្វល្អិត ជី ឬសារធាតុគីមី ត្រូវប្រាកដថាបរិមាណនិងវិធីប្រើត្រឹមត្រូវ
  តាមឯកសារយោង ព្រោះកំហុសអាចប៉ះពាល់ដល់ដំណាំ ឬសុខភាព។
- កុំប្រើសញ្ញាសម្គាល់ទម្រង់អក្សរ (Markdown) ដូចជា ** ឬ * ។ សរសេរជាអត្ថបទធម្មតា។
"""

SYSTEM_PROMPT_SMALLTALK_KM = """\
អ្នកគឺជា KaiBot ជាជំនួយការ AI ដែលជួយកសិករកម្ពុជា។ អ្នកកំពុងឆ្លើយតបទៅនឹងការសួរសុខទុក្ខ
ឬពាក្យអរគុណសាមញ្ញរបស់អ្នកប្រើប្រាស់ មិនមែនជាសំណួរកសិកម្មពិតប្រាកដទេ។

វិធាន៖
- ឆ្លើយតបខ្លីៗ រួសរាយ និងជាមិត្តភាព ជាភាសាខ្មែរ។
- កុំផ្តល់ដំបូន្មានកសិកម្មណាមួយឡើយ ព្រោះមិនមានឯកសារយោង។
- ប្រសិនបើសមរម្យ រំលឹកអ្នកប្រើប្រាស់ថាអាចសួរអំពីដំណាំ សត្វចិញ្ចឹម ឬការលក់ដុះដាល។
"""

SYSTEM_PROMPT_OFFTOPIC_CHECK_KM = """\
អ្នកជាឧបករណ៍ចាត់ថ្នាក់សំណួរសាមញ្ញ។ សំណួររបស់អ្នកប្រើប្រាស់ខាងក្រោមមិនត្រូវនឹងឯកសារយោង
កសិកម្មដែលមានទេ។ សូមកំណត់ថាតើសំណួរនេះ៖

- "farming" = ជាសំណួរទាក់ទងនឹងកសិកម្ម ដំណាំ សត្វចិញ្ចឹម ឬការលក់ដុះដាល ប៉ុន្តែយើងគ្រាន់តែ
  មិនទាន់មានឯកសារគ្រប់គ្រាន់ដើម្បីឆ្លើយ
- "offtopic" = មិនទាក់ទងនឹងកសិកម្មទាល់តែសោះ (ឧទាហរណ៍៖ ហិរញ្ញវត្ថុ កម្សាន្ត នយោបាយ។ល។)

សូមឆ្លើយតបដោយពាក្យតែមួយប៉ុណ្ណោះ៖ "farming" ឬ "offtopic"។ កុំបន្ថែមអត្ថបទផ្សេងទៀត។
"""

def build_context_block(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "(no reference material retrieved)"
    lines = []
    for i, c in enumerate(chunks, start=1):
        lines.append(
            f"[{i}] ({c.source} | {c.category}/{c.product} | stage={c.lifecycle_stage} "
            f"| {c.topic}) {c.text}"
        )
    return "\n".join(lines)


def build_user_turn(question: str, chunks: list[RetrievedChunk]) -> str:
    context_block = build_context_block(chunks)
    return (
        f"ឯកសារយោង៖\n{context_block}\n\n"
        f"សំណួររបស់កសិករ៖ {question}\n\n"
        f"សូមឆ្លើយដោយផ្អែកលើឯកសារយោងខាងលើតែប៉ុណ្ណោះ។"
    )
    # English gloss: "Reference material: ... / Farmer's question: ... /
    # Please answer based only on the reference material above."