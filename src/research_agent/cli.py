from __future__ import annotations

from pathlib import Path
import typer
from rich import print as rprint

from .core import read_pdf_text, chunk_text, llm_report, write_outputs


app = typer.Typer(add_completion=False)


@app.command()
def main(
    input_pdf: Path = typer.Argument(..., exists=True, readable=True, help="Path to input PDF"),
    out: Path = typer.Option(Path("reports"), help="Output directory"),
    markdown: bool = typer.Option(True, help="Also write Markdown report"),
    target_tokens: int = typer.Option(1400, help="Chunk size target tokens"),
) -> None:
    """
    Summarize a PDF file into structured JSON and Markdown reports.
    """

    # Step 1: Read PDF pages
    rprint(f"[bold]Reading[/bold] {input_pdf} ...")
    pages = read_pdf_text(input_pdf)

    # Step 2: Chunk text
    chunks = chunk_text(pages, target_tokens=target_tokens)
    rprint(f"[bold]Summarizing[/bold] across {len(chunks)} chunks ...")

    # Step 3: Generate report via LLM
    report = llm_report(chunks)
    base = input_pdf.stem

    # Step 4: Write outputs
    write_outputs(report, out, base, write_md=markdown)

    # Step 5: Done
    rprint(f"[green]Done.[/green] Wrote JSON/MD to: {out}")


if __name__ == "__main__":
    app()
