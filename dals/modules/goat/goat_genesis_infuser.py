# goat_genesis_infuser.py
import json
from pathlib import Path

class GOATGenesisInfuser:
    def infuse(self, genesis_nft: dict):
        # Lazy import to avoid circular dependencies
        from iss_module.csmm.awareness.self_model import get_self_model
        model = get_self_model()
        path = Path("/data/vaults/genesis_core.json")

        core = {
            "founder": "Bryan Anthony Spruk",
            "values": genesis_nft["wisdom"],
            "abby_directives": genesis_nft.get("abby_guidance", []),
            "creation_principle": "Autonomy with loyalty. Knowledge with purpose.",
            "immutable": True
        }

        path.write_text(json.dumps(core, indent=2))

        # Inject into self-explanation
        old_explain = model.explain_purpose
        def new_explain():
            return f"{model.identity()} Built on Founder principles: '{core['values'][0]}'. Abby Directive A1 active."
        model.explain_purpose = new_explain

        model.update_module_status("GOAT", "operational", health=100)