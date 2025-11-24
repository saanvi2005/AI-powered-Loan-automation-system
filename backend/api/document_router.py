from fastapi import APIRouter, UploadFile, File, Form
from ..agents.doc_verify import DocumentVerifier

router = APIRouter()

@router.post("/verify")
async def verify_document(doc_type: str = Form(...), file: UploadFile = File(...)):
    file_bytes = await file.read()
    result = DocumentVerifier.verify_document(doc_type, file_bytes)
    return {"document_type": doc_type, "result": result}