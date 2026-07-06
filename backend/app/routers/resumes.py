import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resumes import Resume
from app.models.users import User
from app.schemas.resumes import ResumeResponse
from app.utils.oauth2 import get_current_user
from app.utils.pdf import MAX_PDF_BYTES, extract_pdf_text

router = APIRouter(prefix="/resumes", tags=["Resumes"])

UPLOAD_DIR = Path(os.getenv("RESUME_UPLOAD_DIR", "./storage/resumes")).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # --- validate ------------------------------------------------------------
    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(contents) > MAX_PDF_BYTES:
        raise HTTPException(status_code=400, detail="Resume too large (max 5MB)")

    # --- extract text --------------------------------------------------------
    text = extract_pdf_text(contents)
    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract any text from the PDF",
        )

    # --- store file on disk (dev). In prod use object storage. ---------------
    safe_name = f"user_{current_user.id}_{uuid.uuid4().hex}.pdf"
    storage_path = UPLOAD_DIR / safe_name
    storage_path.write_bytes(contents)

    # --- upsert single-latest-resume row ------------------------------------
    resume = db.scalar(select(Resume).where(Resume.user_id == current_user.id))
    if resume is None:
        resume = Resume(
            user_id=current_user.id,
            filename=file.filename or safe_name,
            storage_path=str(storage_path),
            extracted_text=text,
        )
        db.add(resume)
    else:
        # Delete previous file to avoid growing junk on disk.
        try:
            Path(resume.storage_path).unlink(missing_ok=True)
        except Exception:
            pass
        resume.filename = file.filename or safe_name
        resume.storage_path = str(storage_path)
        resume.extracted_text = text
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/me", response_model=ResumeResponse)
def get_my_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.scalar(select(Resume).where(Resume.user_id == current_user.id))
    if resume is None:
        raise HTTPException(status_code=404, detail="No resume uploaded yet")
    return resume


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.scalar(select(Resume).where(Resume.user_id == current_user.id))
    if resume is None:
        raise HTTPException(status_code=404, detail="No resume to delete")
    try:
        Path(resume.storage_path).unlink(missing_ok=True)
    except Exception:
        pass
    db.delete(resume)
    db.commit()
    return None
