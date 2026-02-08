import logging
import time
import uuid
from typing import Optional
from collections import defaultdict

from sqlalchemy.orm import Session
from open_webui.internal.db import Base, get_db, get_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, UniqueConstraint, Index

log = logging.getLogger(__name__)

####################
# DocumentImage DB Schema
####################


class DocumentImage(Base):
    __tablename__ = "document_image"
    id = Column(String, primary_key=True, unique=True)
    file_id = Column(String, nullable=False)
    image_file_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)

    __table_args__ = (
        UniqueConstraint("file_id", "image_file_id", name="uq_file_image"),
        Index("ix_document_image_file_id", "file_id"),
        Index("ix_document_image_image_file_id", "image_file_id"),
        Index("ix_document_image_user_id", "user_id"),
    )


class DocumentImageModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_id: str
    image_file_id: str
    user_id: str
    created_at: Optional[int]
    updated_at: Optional[int]


class DocumentImagesTable:
    def add_image_to_document(
        self,
        file_id: str,
        image_file_id: str,
        user_id: str,
        db: Optional[Session] = None,
    ) -> Optional[DocumentImageModel]:
        with get_db_context(db) as db:
            try:
                now = int(time.time())
                record = DocumentImage(
                    id=str(uuid.uuid4()),
                    file_id=file_id,
                    image_file_id=image_file_id,
                    user_id=user_id,
                    created_at=now,
                    updated_at=now,
                )
                db.add(record)
                db.commit()
                db.refresh(record)
                return DocumentImageModel.model_validate(record)
            except Exception as e:
                log.exception(f"Error adding image to document: {e}")
                return None

    def remove_image_from_document(
        self,
        file_id: str,
        image_file_id: str,
        db: Optional[Session] = None,
    ) -> bool:
        with get_db_context(db) as db:
            try:
                db.query(DocumentImage).filter_by(
                    file_id=file_id, image_file_id=image_file_id
                ).delete()
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error removing image from document: {e}")
                return False

    def get_images_by_file_id(
        self, file_id: str, db: Optional[Session] = None
    ) -> list[DocumentImageModel]:
        with get_db_context(db) as db:
            return [
                DocumentImageModel.model_validate(record)
                for record in db.query(DocumentImage)
                .filter_by(file_id=file_id)
                .order_by(DocumentImage.created_at.asc())
                .all()
            ]

    def get_images_by_file_ids(
        self, file_ids: list[str], db: Optional[Session] = None
    ) -> dict[str, list[dict]]:
        """Batch lookup: returns {file_id: [{image_file_id, filename, content_type}, ...]}"""
        if not file_ids:
            return {}
        with get_db_context(db) as db:
            from open_webui.models.files import File

            results = (
                db.query(DocumentImage, File)
                .join(File, DocumentImage.image_file_id == File.id)
                .filter(DocumentImage.file_id.in_(file_ids))
                .order_by(DocumentImage.created_at.asc())
                .all()
            )

            grouped: dict[str, list[dict]] = defaultdict(list)
            for doc_image, file in results:
                content_type = None
                if file.meta and isinstance(file.meta, dict):
                    content_type = file.meta.get("content_type")
                grouped[doc_image.file_id].append(
                    {
                        "image_file_id": doc_image.image_file_id,
                        "filename": file.filename,
                        "content_type": content_type,
                    }
                )
            return dict(grouped)

    def get_documents_by_image_file_id(
        self, image_file_id: str, db: Optional[Session] = None
    ) -> list[DocumentImageModel]:
        with get_db_context(db) as db:
            return [
                DocumentImageModel.model_validate(record)
                for record in db.query(DocumentImage)
                .filter_by(image_file_id=image_file_id)
                .all()
            ]

    def delete_all_images_for_file(
        self, file_id: str, db: Optional[Session] = None
    ) -> bool:
        with get_db_context(db) as db:
            try:
                db.query(DocumentImage).filter_by(file_id=file_id).delete()
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error deleting all images for file: {e}")
                return False


DocumentImages = DocumentImagesTable()
