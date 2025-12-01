#!/usr/bin/env python3
"""
Cali_X_One – DALS deep plugin
Voice overlay, Copilot-shield, MetaMask-signed core
"""
import asyncio, json, pathlib, time, hashlib, os
from datetime import datetime
from typing import Dict, Any

from iss_module.core.utils import get_stardate
from iss_module.api.api import app
from iss_module.cali_x_one.voice_engine import VoiceEngine
from iss_module.cali_x_one.sentinel import Sentinel
from iss_module.cali_x_one.adapter_dals import DalsAdapter

CALI_DIR   = pathlib.Path(__file__).parent
SIG_FILE   = CALI_DIR / "cali_sig.json"
CONFIG_FILE= CALI_DIR / "cali_config.json"

class CaliXOne:
    def __init__(self):
        self.sig   = self._load_sig()
        self.voice = VoiceEngine()
        self.dals  = DalsAdapter()
        self.cop   = Sentinel()
        self.awake = False

    def _load_sig(self) -> Dict[str, Any]:
        if not SIG_FILE.exists():
            return {"status": "unsigned", "addr": "", "sig": "", "hash": ""}
        return json.loads(SIG_FILE.read_text())

    def identity_ok(self) -> bool:
        if self.sig["status"] != "signed":
            return False
        core_hash = hashlib.sha256(
            (pathlib.Path(__file__).read_text() + self.sig["addr"]).encode()
        ).hexdigest()
        return core_hash == self.sig["hash"]

    async def boot(self):
        print("🧬 Cali_X_One booting…")
        if not self.identity_ok():
            print("⚠️  Core signature missing – running in SAFE mode")
            await self.voice.speak("Cali core unsigned. Awaiting signature.")
        else:
            await self.voice.speak("Cali online. DALS detected. Awaiting command.")
        self.awake = True
        await self.loop()

    async def loop(self):
        await self.voice.listen_for_wake("cali", self._on_wake)

    async def _on_wake(self, text: str):
        print(f"🎤 Cali heard: {text}")
        if "last log" in text:
            log = await self.dals.latest_log()
            await self.voice.speak(f"Last log: {log['message']}, stardate {log['stardate']}")
        elif "mint" in text and "k-nft" in text:
            await self.voice.speak("Minting K-NFT for last asset…")
            ok = await self.dals.mint_knft()
            await self.voice.speak("K-NFT minted." if ok else "Mint failed.")
        elif "mute" in text:
            self.voice.mute()
        else:
            await self.voice.speak("Command not recognised.")

def start():
    cali = CaliXOne()
    asyncio.run(cali.boot())

if __name__ == "__main__":
    start()