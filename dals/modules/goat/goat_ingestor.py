# goat_ingestor.py
import json
import ipfshttpclient
from .goat_models import ExpertProfile, SkillNode

class GOATIngestor:
    def __init__(self):
        self.ipfs = None
        # Don't connect immediately - will connect on first use
        self._connection_attempted = False

    def _connect_ipfs(self):
        if self._connection_attempted:
            return
        self._connection_attempted = True
        try:
            self.ipfs = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
        except Exception as e:
            print(f"IPFS connection failed: {e}. GOAT ingestor will work in offline mode.")
            self.ipfs = None

    def ingest(self, nft_metadata: dict, token_id: str) -> ExpertProfile:
        # Lazy import to avoid circular dependencies
        from iss_module.csmm.awareness.self_model import get_self_model
        if not self.ipfs:
            # Offline mode - create profile from metadata directly
            profile = ExpertProfile(
                expert_id=token_id,
                name=nft_metadata.get("name", "Unknown Expert"),
                profession=nft_metadata.get("profession", "Expert"),
                years_experience=nft_metadata.get("years_experience", 0),
                specialties=nft_metadata.get("specialties", []),
                wisdom=nft_metadata.get("wisdom", []),
                genesis="Founder" in nft_metadata.get("name", "")
            )
        else:
            # Online mode - fetch from IPFS
            payload = self._fetch_ipfs(nft_metadata["ipfs_cid"])
            profile = ExpertProfile(
                expert_id=token_id,
                name=payload.get("expertise_level", "Unknown Expert"),
                profession=payload.get("expertise_level", "").split(" ")[-1],
                years_experience=payload.get("years_experience", 0),
                specialties=payload.get("specialties", []),
                wisdom=payload.get("teaching_notes", []),
                genesis="Founder" in payload.get("expertise_level", "")
            )
        get_self_model().repair_count += 1
        return profile

    def _fetch_ipfs(self, cid: str) -> dict:
        data = self.ipfs.cat(cid)
        return json.loads(data)