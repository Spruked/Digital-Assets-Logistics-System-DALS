"""
Unanswered Query Vault (UQV) Model
Stores queries that returned zero clusters or low confidence
for later SKG training and human review.
"""
from sqlalchemy import Column, String, Text, Float, DateTime, JSON, Integer
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UnansweredQuery(Base):
    """
    Vault for queries that the SKG couldn't answer confidently.
    Used for continuous learning and predicate invention.
    """
    __tablename__ = "unanswered_query"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    session_id = Column(String(36), nullable=False)
    query_text = Column(Text, nullable=False)
    query_vec = Column(JSON)                 # optional embedding
    skg_clusters_returned = Column(Integer, default=0)
    max_cluster_conf = Column(Float, default=0.0)
    worker_name = Column(String(20))         # Regent/Nora/Mark
    vault_reason = Column(String(50))        # "no_cluster"|"low_conf"|"escalated"
    created_at = Column(DateTime, server_default=func.now())
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "query_text": self.query_text,
            "skg_clusters_returned": self.skg_clusters_returned,
            "max_cluster_conf": self.max_cluster_conf,
            "worker_name": self.worker_name,
            "vault_reason": self.vault_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
