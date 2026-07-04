import PyPDF2
from typing import Dict, Any

class DocumentParser:
    def parse_pdf(self, file_path: str) -> str:
        text = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n\n"
        return text

    # Other parsers (docx, xlsx, etc) would go here
    def parse(self, file_path: str, file_type: str) -> str:
        if file_type == "application/pdf":
            return self.parse_pdf(file_path)
        elif file_type == "text/plain":
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        else:
            # Fallback for "all other file types" (.md, .csv, etc) - try to read as UTF-8 text
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                    return file.read()
            except Exception as e:
                raise ValueError(f"Unsupported file type or unreadable binary file: {file_type}. Error: {e}")

parser = DocumentParser()
