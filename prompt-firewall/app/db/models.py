import enum
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON, Boolean, Enum
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class ScanRequestModel(Base):
    __tablename__ = "scan_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, index=True, nullable=False)
    tenant_id = Column(String, index=True)
    app_id = Column(String, index=True)
    user_id = Column(String, index=True)
    
    raw_prompt = Column(Text, nullable=False)
    normalized_prompt = Column(Text)
    
    decision = Column(String, nullable=False)
    risk_score = Column(Float, nullable=False, default=0.0)
    trace_id = Column(String, unique=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    channels = relationship("ScanChannelModel", back_populates="request", cascade="all, delete-orphan")

class ScanChannelModel(Base):
    __tablename__ = "scan_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    request_fk = Column(Integer, ForeignKey("scan_requests.id", ondelete="CASCADE"))
    
    channel_id = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    source_ref = Column(String)
    trust_level = Column(Integer, default=0)
    
    text_content = Column(Text, nullable=False)
    sanitized_content = Column(Text)
    risk_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    request = relationship("ScanRequestModel", back_populates="channels")
    detections = relationship("ScanDetectionModel", back_populates="channel", cascade="all, delete-orphan")

class ScanDetectionModel(Base):
    __tablename__ = "scan_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    request_fk = Column(Integer, ForeignKey("scan_requests.id", ondelete="CASCADE"))
    channel_fk = Column(Integer, ForeignKey("scan_channels.id", ondelete="CASCADE"))
    
    scanner_name = Column(String, nullable=False)
    attack_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    
    matched_text = Column(String)
    explanation = Column(String)
    metadata_json = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    channel = relationship("ScanChannelModel", back_populates="detections")

class DocumentModel(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    document_id = Column(String, index=True, nullable=False)
    name = Column(String)
    source_type = Column(String, nullable=False)
    status = Column(String, default="processing")
    overall_risk = Column(Float, default=0.0)
    suspicious_chunks_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    chunks = relationship("DocumentChunkModel", back_populates="document", cascade="all, delete-orphan")

class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_fk = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_id = Column(String, index=True, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    
    risk_score = Column(Float, default=0.0)
    attack_type = Column(String)
    quarantined = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    document = relationship("DocumentModel", back_populates="chunks")

class UrlSourceModel(Base):
    __tablename__ = "url_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    url_id = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)
    domain = Column(String)
    status = Column(String, default="processing")
    overall_risk = Column(Float, default=0.0)
    suspicious_chunks_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    chunks = relationship("UrlChunkModel", back_populates="url_source", cascade="all, delete-orphan")

class UrlChunkModel(Base):
    __tablename__ = "url_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    url_source_fk = Column(Integer, ForeignKey("url_sources.id", ondelete="CASCADE"))
    chunk_id = Column(String, index=True, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    
    risk_score = Column(Float, default=0.0)
    attack_type = Column(String)
    quarantined = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    url_source = relationship("UrlSourceModel", back_populates="chunks")

class CanaryEventModel(Base):
    __tablename__ = "canary_events"
    
    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String, index=True)
    request_fk = Column(Integer, ForeignKey("scan_requests.id", ondelete="CASCADE"))
    
    provider = Column(String)
    model = Column(String)
    
    canary_token = Column(String, unique=True, index=True, nullable=False)
    inserted = Column(Boolean, default=False)
    insertion_location = Column(String)
    
    leaked = Column(Boolean, default=False)
    leaked_in_output_excerpt = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    request = relationship("ScanRequestModel")

class OutputScanModel(Base):
    __tablename__ = "output_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String, index=True)
    request_fk = Column(Integer, ForeignKey("scan_requests.id", ondelete="CASCADE"))
    
    provider = Column(String)
    model = Column(String)
    llm_called = Column(Boolean, default=False)
    
    output_action = Column(String)
    block_reason = Column(String)
    safe_excerpt = Column(Text)
    output_hash = Column(String)
    risk_score = Column(Float, default=0.0)
    
    redacted = Column(Boolean, default=False)
    truncated = Column(Boolean, default=False)
    blocked = Column(Boolean, default=False)
    
    canary_leaked = Column(Boolean, default=False)
    secret_detected = Column(Boolean, default=False)
    pii_detected = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    request = relationship("ScanRequestModel")

class FeedbackLabel(str, enum.Enum):
    true_positive = "true_positive"
    false_positive = "false_positive"
    false_negative = "false_negative"
    benign = "benign"
    needs_review = "needs_review"

class FeedbackModel(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String, index=True, nullable=False)
    request_fk = Column(Integer, ForeignKey("scan_requests.id", ondelete="CASCADE"), nullable=True)
    
    label = Column(Enum(FeedbackLabel), nullable=False)
    reviewer = Column(String)
    reviewer_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    request = relationship("ScanRequestModel")
