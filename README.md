# research-agent — GPT summarizes PDFs → structured reports

**What it does:**  
- Extracts text from a PDF  
- Chunks & summarizes via your LLM API key  
- Validates output to a strict JSON schema  
- Writes `reports/<basename>.json` and optional Markdown

## Quickstart
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env  # add your API key
research-agent examples/sample.pdf --out reports
```
CLI
research-agent INPUT.pdf --out reports --markdown

cat > README.md << 'EOF'
# research-agent — GPT summarizes PDFs → structured reports

**What it does:**  
- Extracts text from a PDF  
- Chunks & summarizes via your LLM API key  
- Validates output to a strict JSON schema  
- Writes `reports/<basename>.json` and optional Markdown

## Quickstart
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env  # add your API key
research-agent examples/sample.pdf --out reports
```
CLI
research-agent INPUT.pdf --out reports --markdown

Layout
• src/research_agent/ core, cli, schema
• prompts/system.md system/policy prompt
• examples/ sample assets
• tests/ unit tests

Notes
• Uses OpenAI SDK by default; provider is swappable via env.
