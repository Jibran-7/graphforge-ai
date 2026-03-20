import hashlib
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Document, Entity, Relationship
from app.schemas.document import DocumentDetailResponse, DocumentResponse
from app.services.extraction_service import ExtractionService


class DocumentServiceError(Exception):
    pass


class MissingFileError(DocumentServiceError):
    pass


class EmptyFileError(DocumentServiceError):
    pass


class UnsupportedContentTypeError(DocumentServiceError):
    pass


class OversizedFileError(DocumentServiceError):
    pass


class DecodeFailureError(DocumentServiceError):
    pass


class ExtractionFailureError(DocumentServiceError):
    pass


class DocumentNotFoundError(DocumentServiceError):
    pass


class DocumentService:
    SUPPORTED_CONTENT_TYPES = {
        "text/plain": "txt",
        "text/markdown": "md",
    }

    def __init__(self) -> None:
        self.settings = get_settings()
        self.extraction_service = ExtractionService()

    async def _read_upload_bytes(self, file: UploadFile) -> bytes:
        payload = b""

        # Strategy 1: standard async read.
        try:
            payload = await file.read()
        except Exception:
            payload = b""

        if payload:
            return payload

        # Strategy 2: rewind async stream and re-read.
        try:
            await file.seek(0)
            payload = await file.read()
        except Exception:
            payload = b""

        if payload:
            return payload

        # Strategy 3: read directly from underlying sync file object.
        try:
            file.file.seek(0)
            payload = file.file.read()
            if isinstance(payload, str):
                payload = payload.encode("utf-8")
        except Exception:
            payload = b""

        return payload if isinstance(payload, (bytes, bytearray)) else b""

    async def upload_document(self, db: Session, file: UploadFile | None) -> DocumentResponse:
        if file is None or not file.filename or not file.filename.strip():
            raise MissingFileError("File is required.")

        content_type = (file.content_type or "").strip().lower()
        if content_type not in self.SUPPORTED_CONTENT_TYPES:
            raise UnsupportedContentTypeError("Unsupported content type.")

        extension = Path(file.filename).suffix.lower().lstrip(".")
        if not extension:
            extension = self.SUPPORTED_CONTENT_TYPES[content_type]

        allowed_types = {item.lower() for item in self.settings.allowed_file_types}
        if extension not in allowed_types:
            raise UnsupportedContentTypeError("File extension is not allowed.")

        payload = await self._read_upload_bytes(file)

        if not payload:
            raise EmptyFileError("Uploaded file is empty.")

        max_bytes = self.settings.max_upload_size_mb * 1024 * 1024
        if len(payload) > max_bytes:
            raise OversizedFileError("Uploaded file exceeds maximum allowed size.")

        try:
            extracted_text = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DecodeFailureError("Unable to decode file as UTF-8 text.") from exc

        upload_dir = Path(self.settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        safe_stem = Path(file.filename).stem.strip().replace(" ", "_") or "document"
        digest = hashlib.sha256(payload).hexdigest()[:16]
        stored_filename = f"{safe_stem}_{digest}.{extension}"
        stored_path = upload_dir / stored_filename
        stored_path.write_bytes(payload)

        document = Document(
            filename=file.filename.strip(),
            content_type=content_type,
            file_path=str(stored_path),
            file_size=len(payload),
            extracted_text=extracted_text,
        )
        db.add(document)
        db.flush()

        try:
            extraction = self.extraction_service.extract(document_id=document.id, text=extracted_text)
            entity_map: dict[str, Entity] = {}

            for item in extraction["entities"]:
                key = item["name"].strip().lower()
                if key in entity_map:
                    continue
                entity = Entity(
                    document_id=document.id,
                    name=item["name"],
                    entity_type=item["entity_type"],
                )
                db.add(entity)
                db.flush()
                entity_map[key] = entity

            seen_relationships: set[tuple[int, int, str, str]] = set()
            for item in extraction["relationships"]:
                source_key = item["source_name"].strip().lower()
                target_key = item["target_name"].strip().lower()

                if source_key not in entity_map:
                    source_entity = Entity(
                        document_id=document.id,
                        name=item["source_name"],
                        entity_type=self.extraction_service.infer_entity_type(item["source_name"]),
                    )
                    db.add(source_entity)
                    db.flush()
                    entity_map[source_key] = source_entity

                if target_key not in entity_map:
                    target_entity = Entity(
                        document_id=document.id,
                        name=item["target_name"],
                        entity_type=self.extraction_service.infer_entity_type(item["target_name"]),
                    )
                    db.add(target_entity)
                    db.flush()
                    entity_map[target_key] = target_entity

                source_entity = entity_map[source_key]
                target_entity = entity_map[target_key]

                relation_key = (
                    source_entity.id,
                    target_entity.id,
                    item["relation_type"],
                    item["evidence_text"].strip(),
                )
                if relation_key in seen_relationships:
                    continue
                seen_relationships.add(relation_key)

                relationship = Relationship(
                    document_id=document.id,
                    source_entity_id=source_entity.id,
                    target_entity_id=target_entity.id,
                    relation_type=item["relation_type"],
                    evidence_text=item["evidence_text"],
                )
                db.add(relationship)

            db.commit()
            db.refresh(document)
        except Exception as exc:
            db.rollback()
            raise ExtractionFailureError("Failed to extract entities and relationships.") from exc

        return DocumentResponse.model_validate(document)

    def list_documents(self, db: Session) -> list[DocumentResponse]:
        documents = db.query(Document).order_by(Document.uploaded_at.desc()).all()
        return [DocumentResponse.model_validate(item) for item in documents]

    def get_document(self, db: Session, document_id: int) -> DocumentDetailResponse:
        document = db.query(Document).filter(Document.id == document_id).first()
        if document is None:
            raise DocumentNotFoundError("Document not found.")
        return DocumentDetailResponse.model_validate(document)
