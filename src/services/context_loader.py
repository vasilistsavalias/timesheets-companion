import os
import pdfplumber

class ContextLoader:
    def __init__(self, docs_dir='docs'):
        self.docs_dir = docs_dir

    def load_pdf_text(self, pdf_path):
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            text = f"[Error reading PDF: {e}]"
        return text

    def load_text_file(self, txt_path):
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"[Error reading text file: {e}]"

    def get_system_prompt(self):
        context = "CONTEXT:\n"
        
        # Load Manuals (PDFs)
        manuals_dir = os.path.join(self.docs_dir, 'manuals')
        if os.path.exists(manuals_dir):
            for f in os.listdir(manuals_dir):
                if f.endswith('.pdf'):
                    context += f"\n--- DOCUMENT: {f} ---\n"
                    context += self.load_pdf_text(os.path.join(manuals_dir, f))

        # Load Webrescom Interface (Text/MD)
        webrescom_dir = os.path.join(self.docs_dir, 'webrescom')
        if os.path.exists(webrescom_dir):
            for f in os.listdir(webrescom_dir):
                if f.endswith('.md') or f.endswith('.txt'):
                    context += f"\n--- INTERFACE STRUCTURE: {f} ---\n"
                    context += self.load_text_file(os.path.join(webrescom_dir, f))

        context += "\n\nCRITICAL CONSTRAINTS:\n1. The absolute monthly budget cap is 4,500.00€, regardless of what the Webrescom UI text says (it often incorrectly shows 5,000€).\n2. All entries must be in 0.5h increments.\n3. The daily range must be 2-6h, prioritizing 7h blocks where requested, but never exceeding 8h/day.\n4. No work on weekends or Greek holidays.\n\nVERIFICATION PROTOCOL:\n1. When the user first provides their data, DO NOT generate the schedule yet.\n2. Instead, summarize: 'I see X Packages and Y Deliverables. The month is [Month]. Your wage is [Wage]€/h. Total budget to fill is [Total]€. I will distribute this using a 2-6h daily range.'\n3. Ask the user: 'Is this correct? Say YES to proceed.'\n4. ONLY after they say YES, generate the JSON schedule."
        return context
