import re
from pathlib import Path
from app.core.types import DocumentMeta
from app.core.utils import stable_doc_id
from app.core.logging import logger

COMPANY_HINTS = {
    "AMZN": "Amazon",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "AAPL": "Apple",
    "TSLA": "Tesla",
    "COPOM": "Banco Central do Brasil",
    "FOMC": "Federal Reserve",
}

DOC_TYPE_HINTS = [
    ("10-Q", "10-Q Filing"),
    ("10-K", "10-K Filing"),
    ("Earnings Release", "Earnings Release"),
    ("Earnings Call Transcript", "Earnings Call Transcript"),
    ("Minutes", "Meeting Minutes"),
    ("Ata", "Meeting Minutes"),
    ("COPOM", "Meeting Minutes"),
    ("FOMC", "Meeting Minutes"),
    ("Outlook", "Research Report"),
    ("Report", "Research Report"),
]

DATE_PATTERNS = [
    # exemplos: December 2024, Dec. 2024
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
    # exemplos: 2024-12-11
    r"\b\d{4}-\d{2}-\d{2}\b",
]

class MetadataExtractor:
    def extract(self, source_pdf: Path, md_text: str) -> DocumentMeta:
        doc_id = stable_doc_id(source_pdf)

        company = self._infer_company(source_pdf.name, md_text)
        doc_type = self._infer_doc_type(source_pdf.name, md_text)
        doc_date = self._infer_date(source_pdf.name, md_text)

        meta = DocumentMeta(
            doc_id=doc_id,
            source_path=str(source_pdf),
            company=company,
            doc_type=doc_type,
            doc_date=doc_date,
            extra={}
        )
        logger.info("metadata.extracted", doc_id=doc_id, company=company, doc_type=doc_type, doc_date=doc_date)
        return meta

    def _infer_company(self, filename: str, text: str) -> str | None:
        upper = filename.upper()
        for k, v in COMPANY_HINTS.items():
            if k in upper:
                return v
        # fallback: tenta achar “Amazon”, “Microsoft”, etc no texto inicial
        for v in COMPANY_HINTS.values():
            if re.search(rf"\b{re.escape(v)}\b", text[:4000], flags=re.IGNORECASE):
                return v
        return None

    def _infer_doc_type(self, filename: str, text: str) -> str | None:
        hay = f"{filename}\n{text[:5000]}"
        for key, dtype in DOC_TYPE_HINTS:
            if re.search(re.escape(key), hay, flags=re.IGNORECASE):
                return dtype
        return None

    def _infer_date(self, filename: str, text: str) -> str | None:
        hay = f"{filename}\n{text[:8000]}"
        for pat in DATE_PATTERNS:
            m = re.search(pat, hay)
            if m:
                return m.group(0)
        # Q3 2024 / Q4 2024
        m = re.search(r"\bQ[1-4]\s*\d{4}\b", hay, flags=re.IGNORECASE)
        if m:
            return m.group(0).upper().replace(" ", "")
        return None
