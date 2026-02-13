from pathlib import Path
from src.app.core.utils import ensure_dir
from src.app.core.logging import logger

class PdfToMarkdownConverter:
    """
    Converte PDF -> Markdown usando Docling.
    Sem OCR (você explicitou que não quer OCR).
    """

    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        ensure_dir(out_dir)

    def convert(self, pdf_path: Path) -> Path:
        """
        Retorna o caminho do .md gerado.
        """
        md_path = self.out_dir / f"{pdf_path.stem}.md"

        # Docling (ajuste conforme sua versão instalada)
        # A ideia aqui é: parsear o PDF e exportar Markdown preservando tabelas.
        try:
            from docling.document_converter import DocumentConverter  # type: ignore
        except Exception as e:
            raise RuntimeError("Docling não disponível. Instale e valide a API do seu ambiente.") from e

        logger.info("pdf_to_md.start", pdf=str(pdf_path), md=str(md_path))
        converter = DocumentConverter()  # configure conforme necessário, sem OCR

        doc = converter.convert(str(pdf_path))  # docling retorna um objeto documento
        md_text = doc.document.export_to_markdown()  # API típica; ajuste se necessário

        md_path.write_text(md_text, encoding="utf-8")
        logger.info("pdf_to_md.done", pdf=str(pdf_path), md=str(md_path))
        return md_path
