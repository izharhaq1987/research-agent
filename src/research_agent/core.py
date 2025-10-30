from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pypdf import PdfReader
import tiktoken
from openai import OpenAI

from .schema import Report, Section




def read_pdf_text(pdf_path: Path) -> List[str]:
    reader = PdfReader(str(pdf_path))
    pages: List[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text.strip())
    return pages


def chunk_text(pages: List[str], target_tokens: int = 1400) -> List[str]:
    enc = tiktoken.get_encoding("cl100k_base")
    chunks: List[str] = []
    buffer: List[str] = []
    token_count = 0

    for page in pages:
        page_tokens = len(enc.encode(page))
        # flush if adding this page would exceed target
        if token_count and (token_count + page_tokens > target_tokens):
            chunks.append("\n\n".join(buffer))
            buffer = []
            token_count = 0
        buffer.append(page)
        token_count += page_tokens

    if buffer:
        chunks.append("\n\n".join(buffer))
    return chunks


def llm_report(chunks: List[str]) -> Report:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    max_tokens = int(os.getenv("MAX_TOKENS", "3000"))
    temperature = float(os.getenv("TEMPERATURE", "0.1"))

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing (see .env.example)")

    client = OpenAI(api_key=api_key)

    system = Path("prompts/system.md").read_text(encoding="utf-8")
    chunks_text = "\n\n".join(f"[Chunk {i+1}]\n{ch}" for i, ch in enumerate(chunks))

    user = (
        "Summarize the following PDF chunks. Return ONLY valid JSON with fields: "
        "{doc_title, doc_meta, key_findings:{title,bullets[]}, methodology:{title,bullets[]}, "
        "limitations:{title,bullets[]}, important_quotes:[{page?, text}], "
        "entities[], topics[], pages_covered?}. "
        "Use nulls/empties when unknown.\n\n"
        f"{chunks_text}"
    )

    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )

    raw = resp.choices[0].message.content
    data = json.loads(raw)

    # --- normalize fields ---
    from typing import Any, Dict

    def _as_dict(v: Any) -> Dict[str, Any]:
        return v if isinstance(v, dict) else {}

    def _as_list(v: Any) -> list:
        return v if isinstance(v, list) else []

    def _section(v: Any, title: str):
        v = v or {}
        return Section(
            title=(v.get("title") or title),
            bullets=_as_list(v.get("bullets")),
        )

    data["doc_title"] = data.get("doc_title") or "Untitled"
    data["doc_meta"] = _as_dict(data.get("doc_meta"))
    data["key_findings"] = _section(data.get("key_findings"), "Key Findings")
    data["methodology"] = _section(data.get("methodology"), "Methodology")
    data["limitations"] = _section(data.get("limitations"), "Limitations")
    data["important_quotes"] = _as_list(data.get("important_quotes"))
    data["entities"] = _as_list(data.get("entities"))
    data["topics"] = _as_list(data.get("topics"))
    data["pages_covered"] = data.get("pages_covered")

    return Report(**data)

# ↓↓↓ place this at top-level, not inside llm_report ↓↓↓
def write_outputs(report: Report, out_dir: Path, base: str, write_md: bool = True) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"{base}.json"
    json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    if not write_md:
        return

    md_path = out_dir / f"{base}.md"
    lines: List[str] = []
    lines.append(f"# {report.doc_title}")
    lines.append("")

    if report.doc_meta:
        lines.append("**Metadata**")
        for k, v in report.doc_meta.items():
            lines.append(f"- **{k}**: {v}")
        lines.append("")

    def sect(title: str, bullets: List[str]) -> None:
        lines.append(f"## {title}")
        for b in bullets:
            lines.append(f"- {b}")
        lines.append("")

    sect(report.key_findings.title, report.key_findings.bullets)
    sect(report.methodology.title,   report.methodology.bullets)
    sect(report.limitations.title,   report.limitations.bullets)

    if report.important_quotes:
        lines.append("## Important quotes")
        for q in report.important_quotes:
            prefix = f"(p. {q.page}) " if q.page is not None else ""
            lines.append(f"> {prefix}{q.text}")
        lines.append("")

    if report.entities:
        lines.append("**Entities:** " + ", ".join(report.entities))
    if report.topics:
        lines.append("\n**Topics:** " + ", ".join(report.topics))
    if report.pages_covered is not None:
        lines.append(f"\n**Pages covered:** {report.pages_covered}")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

