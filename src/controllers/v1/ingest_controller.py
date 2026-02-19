import json
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.services.ingest_service import IngestService

logger = logging.getLogger(__name__)
ingestion_router = APIRouter(tags=["ingestion"])


def get_ingest_service() -> IngestService:
    return IngestService()


@ingestion_router.post("/ingest/json/")
async def ingest_json_file(
    file: UploadFile = File(...),
    ingest_service: IngestService = Depends(get_ingest_service),
):
    """
    Ingest JSON from an uploaded file.
    """
    try:
        logger.info(f"Starting JSON file ingestion: {file.filename}")
        content = await file.read()

        result = await ingest_service.ingest_file_content(
            content=content, filename=file.filename
        )

        logger.info(f"JSON file ingestion completed successfully: {file.filename}")
        return JSONResponse(
            status_code=200,
            content={"message": "JSON file ingested successfully", "result": result},
        )

    except json.JSONDecodeError:
        logger.error(f"Invalid JSON file uploaded: {file.filename}")
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    except Exception as e:
        logger.error(f"Error during JSON file ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
