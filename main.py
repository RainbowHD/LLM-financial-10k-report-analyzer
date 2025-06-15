import os
import json
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
import PyPDF2
from google import genai
from weasyprint import HTML
from markdown2 import markdown

# Define pathes 
BASE_DIR = os.path.dirname(__file__)
REPORTS_FOLDER = os.path.join(BASE_DIR, 'reports/ready_to_read')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'reports/completed_report')

################################################################################
####################     INPUT BELOW YOUR API KEY      #########################
################################################################################
your_gemini_api_key_here = "AIzaSyCStVqU8JjQtO_Dj2XeUVnUSwn7HjcCJuI"  ##########
################################################################################
#####################    INPUT ABOVE YOUR API KEY      #########################
################################################################################

class Reader():
    """Reads text from each page individually."""

    @staticmethod
    def load_files(path):
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return "".join(page.extract_text() or "" for page in reader.pages)

class AnnualReport(BaseModel): 
    """Stores prompts for specific variables."""

    company_name: str = Field(
        description='The name of the company as reported in the 10-K'
    )
    auditor: Optional[str] = Field(
        None, description='Name of the external auditor'
    )
    business_description: Optional[str] = Field(
        None, description='Company’s business overview (Item 1)'
    )
    filing_date: datetime = Field(
        ..., description='Date when the 10-K was filed with the SEC'
    )
    risk_factors: Optional[list[str]] = Field(
        None, description='Key risk factors (Item 1A)'
    )
    total_liabilities: Optional[float] = Field(
        None,
        description=(
            'Total liabilities for the fiscal year 2024 (in USD).'
            'See CONSOLIDATED BALANCE SHEETS.'
        ),
    )
    total_equity: Optional[float] = Field(
        None, description='Total equity for the fiscal year 2024 (in USD)'
    )
    total_employees: Optional[int] = Field(
        None, description='Number of employees for the fiscal year 2024'
    )
    retained_earnings: Optional[float] = Field(
        None, description='Retained earnings for the fiscal year 2024 (in USD)'
    )
    net_debt: Optional[float] = Field(
        None, description='Net debt for the fiscal year 2024 (in USD)'
    )
    goodwill: Optional[float] = Field(
        None, description='Goodwill for the fiscal year 2024 (in USD)'
    )
    total_revenue: Optional[int] = Field(
        None, description='Total revenue for the fiscal year 2024 (in USD)'
    )
    gross_margin: Optional[float] = Field(
        None, description='Gross margin for the fiscal year 2024 (in %)'
    )
    operating_income: Optional[float] = Field(
        None, description='Operating income for the fiscal year 2024 (in USD)'
    )
    net_income: Optional[float] = Field(
        None, description='Net income for the fiscal year 2024 (in USD)'
    )
    ebitda: Optional[float] = Field(
        None, description='EBITDA for the fiscal year 2024 (in USD)'
    )
    cash_from_operations: Optional[float] = Field(
        None,
        description=(
            'Net cash generated or used by core business activities during '
            '2024 (in USD)'
        ),
    )
    cash_from_investing: Optional[float] = Field(
        None,
        description=(
            'Net cash used for or provided by investment activities, '
            'including purchase or sale of long-term assets during 2024 (in USD)'
        ),
    )
    cash_from_financing: Optional[float] = Field(
        None,
        description=(
            'Net cash received from or paid to finance the business during '
            '2024 (in USD)'
        ),
    )
    free_cash_flowshare: Optional[float] = Field(
        None,
        description=(
            'Free cash flow per share for 2024 (in USD)'
        ),
    )

class Gemini_pairing(): 
    """Initializes connections, shemas and handles requests."""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.schema = json.dumps(
            AnnualReport.model_json_schema(), indent=2, ensure_ascii=False
        )

    def build_promt(self, report_text) -> str:
        return (
            f'Analyze the following annual report (10-K) and '
            f'fill the data model based on it:\n\n'
            f'{report_text}\n\n'
            f'The output must match this JSON schema exactly:\n'
            f'{self.schema}\n\n'
            'Instructions:\n'
            '- Carefully analyze all numerical values.\n'
            '- Only include fields defined in the schema.\n'
            '- Respond only with a valid JSON object.'
        )
    
    def send_request(self, report_text: str) -> AnnualReport: 
        prompt = self.build_promt(report_text)
        response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': AnnualReport
                }, 
            )
        return response.parsed

class Converter:
    """Converts the annual report to markdown and PDF."""

    @staticmethod
    def convert_to_pdf(report: AnnualReport, output_path: str):
        lines = [
            f"<div align='center'><h1>Annual Report: {report.company_name}</h1></div>"
        ]

        def add(label, value, prefix="", suffix="", fmt="{}"):
            if value is not None:
                try:
                    formatted = fmt.format(value)
                except Exception:
                    formatted = str(value)
                lines.append(f"- **{label}:** {prefix}{formatted}{suffix}")

        add("Business description", report.business_description)
        add("Auditor", report.auditor)
        add(
            "Filling date",
            report.filing_date.strftime("%Y-%m-%d")
            if report.filing_date else None
        )

        add("Total Revenue", report.total_revenue, prefix="$", fmt="{:,.2f}")
        add("Total liabilities", report.total_liabilities, prefix="$", fmt="{:,.2f}")
        add("Total equity", report.total_equity, prefix="$", fmt="{:,.2f}")
        add("Total employees", report.total_employees)

        add("Retained earnings", report.retained_earnings, prefix="$", fmt="{:,.2f}")
        add("Net debt", report.net_debt, prefix="$", fmt="{:,.2f}")
        add("Goodwill", report.goodwill, prefix="$", fmt="{:.2f}")

        add("Gross margin", report.gross_margin, suffix="%", fmt="{:.2f}")
        add("Operating income", report.operating_income, prefix="$", fmt="{:.2f}")
        add("Net income", report.net_income, prefix="$", fmt="{:,.2f}")
        add("EBITDA", report.ebitda, prefix="$", fmt="{:,.2f}")

        add("Cash from operations", report.cash_from_operations, prefix="$", fmt="{:,.2f}")
        add("Cash from investing", report.cash_from_investing, prefix="$", fmt="{:,.2f}")
        add("Cash from financing", report.cash_from_financing, prefix="$", fmt="{:,.2f}")
        add("Cashflow/share", report.free_cash_flowshare, prefix="$", fmt="{:.2f}")

        add("Risk factors", ", ".join(report.risk_factors) if report.risk_factors else None)

        html = markdown("\n\n".join(lines))
        HTML(string=html).write_pdf(output_path)

def main():
    gemini = Gemini_pairing(api_key=your_gemini_api_key_here)
    pdf_reader = Reader()

    for filename in os.listdir(REPORTS_FOLDER):                 # Iterate through every filename in a given folder 
        if not filename.endswith(".pdf"): 
            continue

        path = os.path.join(REPORTS_FOLDER, filename)
        text = pdf_reader.load_files(path)                      # Extract text from PDF

        try: 
            report = gemini.send_request(text)                  # Send text to Gemini 
        except Exception as e: 
            print(f"Error processing {filename}: {e}")
            continue

        name = (
            report.company_name.replace(" ", "_")
            .replace(",", "")
            .replace(".", "")
            .lower()
        )

        output_filename = f"annual_report_{name}_10k.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        Converter.convert_to_pdf(report, output_path)           # Convert the response to HTML and save it as a PDF
        print(f"\nSaved to: {output_path}")

# Starting programm 
if __name__ == "__main__":
    main()