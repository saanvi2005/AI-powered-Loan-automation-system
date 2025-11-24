import easyocr
import re
import io
from PIL import Image
import numpy as np

class DocumentVerifier:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    @staticmethod
    def extract_text(file_bytes):
        verifier = DocumentVerifier()
        image = Image.open(io.BytesIO(file_bytes))
        image_np = np.array(image)
        results = verifier.reader.readtext(image_np)
        text = ' '.join([result[1] for result in results])
        return text

    @staticmethod
    def verify_pan(text):
        pattern = r"[A-Z]{5}[0-9]{4}[A-Z]"
        match = re.search(pattern, text)
        return bool(match)

    @staticmethod
    def verify_aadhaar(text):
        digits = re.findall(r"\b\d{4}\s\d{4}\s\d{4}\b", text)
        return len(digits) > 0

    @staticmethod
    def verify_salary_slip(text):
        keywords = ["Basic Pay", "HRA", "Gross Salary", "Net Salary", "Basic Salary", "Bank name", "allowances"]
        score = sum(k.lower() in text.lower() for k in keywords)
        return score >= 2  # minimum 2 keywords

    @staticmethod
    def verify_document(doc_type, file_bytes):
        text = DocumentVerifier.extract_text(file_bytes)

        if doc_type == "pan":
            return {"pan_valid": DocumentVerifier.verify_pan(text)}

        if doc_type == "aadhaar":
            return {"aadhaar_valid": DocumentVerifier.verify_aadhaar(text)}

        if doc_type == "salary_slip":
            return {"salary_slip_valid": DocumentVerifier.verify_salary_slip(text)}

        return {"error": "Invalid document type"}