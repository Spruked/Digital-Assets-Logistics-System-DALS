import aiohttp, os
from iss_module.core.utils import get_stardate

DALS_BASE = os.getenv("DALS_BASE", "http://localhost:8003")

class DalsAdapter:
    async def latest_log(self):
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{DALS_BASE}/api/v1/vault/query",
                             params={"limit": 1, "order": "desc"}) as r:
                data = await r.json()
                entry = data["entries"][0]
                return {"message": entry["message"], "stardate": entry["stardate"]}

    async def mint_knft(self) -> bool:
        # placeholder – calls TrueMark/Alpha mint endpoint next phase
        print("🍃 Mint K-NFT stub – will wire to mint engine")
        return True