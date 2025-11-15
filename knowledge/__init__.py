# knowledge/__init__.py
"""
Knowledge Immortality Engine
Phase 11-A2: Complete knowledge preservation pipeline

This package provides the full end-to-end system for preserving human expertise
as blockchain-verified NFTs. The pipeline includes:

1. AI Interview Engine - Profession-specific knowledge capture
2. Knowledge Structurer - Data extraction and categorization
3. IPFS Packager - Decentralized storage with cryptographic integrity
4. NFT Metadata Builder - ERC-721 compatible metadata and certificates
5. Pipeline Orchestrator - Complete A→B→C→D→MINT workflow

Usage:
    from knowledge.nft_builder import KnowledgeNFTBuilder

    builder = KnowledgeNFTBuilder()
    result = builder.run_interactive("software_engineer", "React")

    # Knowledge is now immortalized as an NFT-ready package
"""

from .nft_builder import KnowledgeNFTBuilder
from .interview_engine import KnowledgeInterviewEngine
from .structurer import KnowledgeStructurer
from .ipfs_packager import IPFSPackager
from .nft_metadata import NFTMetadataBuilder

__version__ = "1.0.0"
__author__ = "Caleon Prime - Knowledge Immortality Engine"

__all__ = [
    "KnowledgeNFTBuilder",
    "KnowledgeInterviewEngine",
    "KnowledgeStructurer",
    "IPFSPackager",
    "NFTMetadataBuilder"
]