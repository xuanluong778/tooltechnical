from pathlib import Path

p = Path(__file__).resolve().parents[1] / "app/services/llm_content_writer.py"
text = p.read_text(encoding="utf-8")
start = text.index("def _build_instructions(")
end = text.index("\ndef _openai_chat_completion(", start)
new_fn = '''def _build_instructions(
    *,
    field: str,
    target_word_count: int | None = None,
    primary_keyword: str = "",
    llm_mode: str = "auto",
    user_outline_present: bool = False,
) -> str:
    """Delegate SEO field prompts to seo_content_prompt (Helpful Content + EEAT)."""
    from app.services.seo_content_prompt import build_llm_field_instructions

    return build_llm_field_instructions(
        field=field,
        target_word_count=target_word_count,
        primary_keyword=primary_keyword,
        llm_mode=llm_mode,
        user_outline_present=user_outline_present,
    )

'''
p.write_text(text[:start] + new_fn + text[end:], encoding="utf-8")
print("OK")
