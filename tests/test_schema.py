from research_agent.schema import Report, Section

def test_report_model_roundtrip():
    rpt = Report(
        doc_title="Sample",
        doc_meta={"author": "Unknown"},
        key_findings=Section(title="Key findings", bullets=["A", "B"]),
        methodology=Section(title="Method", bullets=["M1"]),
        limitations=Section(title="Limitations", bullets=[]),
        important_quotes=[],
        entities=[],
        topics=[],
        pages_covered=2
    )
    js = rpt.model_dump_json()
    assert "Sample" in js
