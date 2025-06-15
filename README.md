# LLM Financial 10-K Report Analyzer

**This project uses Gemini-2.0-flash to extract, analyze, and generate summaries from 10-K financial reports in PDF format, following the specified structure:**
> - "Business description"	str or None
> - "Auditor"	str or None
> - "Filling date"	str (formatted "YYYY-MM-DD") or None
> - "Total Revenue"	float or int or None
> - "Total liabilities"	float or int or None
> - "Total equity"	float or int or None
> - "Total employees"	int or None
> - "Retained earnings"	float or int or None
> - "Net debt"	float or int or None
> - "Goodwill"	float or int or None
> - "Gross margin"	float or None
> - "Operating income"	float or int or None
> - "Net income"	float or int or None
> - "EBITDA"	float or int or None
> - "Cash from operations"	float or int or None
> - "Cash from investing"	float or int or None
> - "Cash from financing"	float or int or None
> - "Cashflow/share"	float or None
> - "Risk factors"	str (comma-separated) or None

## Features
- PDF parsing with PyPDF2
- Structured data extraction using Gemini
- Markdown and PDF report generation

## Setup
```bash
pip install -r requirements.txt
python main.py
