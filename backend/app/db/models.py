from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    extracted_text = Column(Text, nullable=True)

    entities = relationship("Entity", back_populates="document", cascade="all, delete-orphan")
    relationships = relationship(
        "Relationship",
        back_populates="document",
        cascade="all, delete-orphan",
        foreign_keys="Relationship.document_id",
    )


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("Document", back_populates="entities")
    source_relationships = relationship(
        "Relationship",
        back_populates="source_entity",
        foreign_keys="Relationship.source_entity_id",
    )
    target_relationships = relationship(
        "Relationship",
        back_populates="target_entity",
        foreign_keys="Relationship.target_entity_id",
    )


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    source_entity_id = Column(Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    target_entity_id = Column(Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type = Column(String(100), nullable=False, index=True)
    evidence_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("Document", back_populates="relationships", foreign_keys=[document_id])
    source_entity = relationship("Entity", back_populates="source_relationships", foreign_keys=[source_entity_id])
    target_entity = relationship("Entity", back_populates="target_relationships", foreign_keys=[target_entity_id])
