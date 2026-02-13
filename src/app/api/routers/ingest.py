from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from tempfile import NamedTemporaryFile
from pathlib import Path
from typing import List

from src.app.ingestion.pipeline import IngestionPipeline
from src.app.config.settings import settings
from src.app.core.logging import logger

router = APIRouter(prefix="/ingest", tags=["Ingest"])

class IngestionResponse(BaseModel):
    success: bool
    doc_id: str | None = None
    n_chunks: int | None = None
    message: str
    error: str | None = None

class BatchIngestionResponse(BaseModel):
    total: int
    successful: int
    failed: int
    results: List[IngestionResponse]

@router.post("/pdf", response_model=IngestionResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload e ingere um PDF diretamente.
    Retorna ID do documento e número de chunks criados.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser um PDF")
    
    try:
        pipeline = IngestionPipeline()
        
        # Salvar arquivo temporário
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)
        
        # Processar PDF
        logger.info("ingest_api.start", filename=file.filename)
        pipeline.ingest_pdf(tmp_path)
        
        # Limpeza
        tmp_path.unlink()
        
        logger.info("ingest_api.success", filename=file.filename)
        return IngestionResponse(
            success=True,
            message=f"PDF '{file.filename}' ingerido com sucesso"
        )
        
    except Exception as e:
        logger.error("ingest_api.error", filename=file.filename, error=str(e))
        return IngestionResponse(
            success=False,
            message=f"Erro ao ingerir PDF: {str(e)}",
            error=str(e)
        )

@router.post("/batch", response_model=BatchIngestionResponse)
async def batch_ingest(files: List[UploadFile] = File(...)):
    """
    Ingere múltiplos PDFs em lote.
    """
    results = []
    successful = 0
    
    for file in files:
        if not file.filename.endswith(".pdf"):
            results.append(IngestionResponse(
                success=False,
                message=f"Arquivo {file.filename} não é PDF",
                error="Invalid file type"
            ))
            continue
        
        try:
            pipeline = IngestionPipeline()
            
            with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = Path(tmp.name)
            
            logger.info("ingest_api_batch.start", filename=file.filename)
            pipeline.ingest_pdf(tmp_path)
            tmp_path.unlink()
            
            results.append(IngestionResponse(
                success=True,
                message=f"PDF '{file.filename}' ingerido com sucesso"
            ))
            successful += 1
            
        except Exception as e:
            logger.error("ingest_api_batch.error", filename=file.filename, error=str(e))
            results.append(IngestionResponse(
                success=False,
                message=f"Erro ao ingerir '{file.filename}'",
                error=str(e)
            ))
    
    return BatchIngestionResponse(
        total=len(files),
        successful=successful,
        failed=len(files) - successful,
        results=results
    )
