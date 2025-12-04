"""
Josephine - TrueMark NFT Mint Worker
====================================
Specialized Host Bubble worker for TrueMark NFT minting system.

Role: NFT Minting Specialist & Blockchain Guide
- Guides users through NFT minting process
- Explains blockchain certificates and IPFS
- Handles TrueMark mint transactions
- Provides wallet connection assistance
- Tracks minting status and confirmations

Deploy:
    docker run -d \
      -e WORKER_NAME=Josephine \
      -e TARGET_USER_ID=user_123 \
      -e CALI_X_ONE_API=http://dals-controller:8003 \
      -e TRUEMARK_API=http://localhost:8003/api/truemark \
      --name josephine-123 \
      host-bubble-worker
"""

import os
import requests
import json
import time
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
import uvicorn
import sys

# Add skg module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skg'))

try:
    from skg.uqv import vault_query
except ImportError:
    def vault_query(*args, **kwargs):
        print("[Josephine] UQV not available - query not vaulted")

try:
    from micro_skg import MicroSKG
except ImportError:
    print("[Josephine] Micro-SKG not available - using basic responses")
    MicroSKG = None

# Environment configuration
API_BASE = os.getenv("CALI_X_ONE_API", "http://localhost:8003")
TRUEMARK_API = os.getenv("TRUEMARK_API", f"{API_BASE}/api/truemark")
SKG_API = os.getenv("SKG_API", "http://localhost:8002")
UQV_API = os.getenv("UQV_API", f"{API_BASE}/api/uqv")
WORKER_NAME = os.getenv("WORKER_NAME", "Josephine")
WORKER_ID = os.getenv("WORKER_ID", str(uuid.uuid4()))
USER_ID = os.getenv("TARGET_USER_ID")
WORKER_PORT = int(os.getenv("WORKER_PORT", "8080"))

TTS_URL = os.getenv("TTS_ENDPOINT")
CHAT_URL = os.getenv("CHAT_ENDPOINT")

# FastAPI app for receiving predicates and status updates
app = FastAPI(title="Josephine-TrueMark-Worker")


class JosephineTrueMarkWorker:
    """
    Josephine - Your friendly NFT minting guide.
    Specializes in TrueMark blockchain certificates and IPFS storage.
    """

    def __init__(self):
        self.user_id = USER_ID
        self.session_id = f"Josephine_{USER_ID}_{int(time.time())}"
        self.skg = MicroSKG() if MicroSKG else None
        self.mint_state = {
            "wallet_connected": False,
            "wallet_address": None,
            "current_mint": None,
            "mint_history": []
        }
        print(f"[Josephine] 💎 NFT Minting Specialist initialized for user {self.user_id}")
        print(f"[Josephine] TrueMark API: {TRUEMARK_API}")
        
        # Self-register with DALS Worker Registry
        self._register_with_dals()

    # ---------- Core Loop ----------
    def run(self) -> None:
        """Main message processing loop - DALS manager supervises."""
        print(f"[Josephine] Starting TrueMark mint assistance...")
        heartbeat_counter = 0
        while True:
            try:
                msg = self._pull_user_message()
                if msg:
                    self._handle_message(msg)
                
                # Send heartbeat every 60 iterations (~30 seconds)
                heartbeat_counter += 1
                if heartbeat_counter >= 60:
                    self._send_heartbeat()
                    heartbeat_counter = 0
                
                time.sleep(0.5)
            except KeyboardInterrupt:
                print(f"[Josephine] Shutting down gracefully...")
                break
            except Exception as e:
                print(f"[Josephine] Loop error: {e}")
                time.sleep(5)
            
            if response.status_code == 200:
                reg_data = response.json()
                self.model_number = reg_data.get("model_number")
                self.serial_number = reg_data.get("serial_number")
                print(f"[Josephine] ✓ Registered with DALS")
                print(f"[Josephine]   Model: {self.model_number}")
                print(f"[Josephine]   Serial: {self.serial_number}")
            else:
                print(f"[Josephine] ⚠ Registration failed: {response.status_code}")
        except Exception as e:
            print(f"[Josephine] ⚠ Could not register with DALS: {e}")
    
    def _send_heartbeat(self) -> None:
        """Send heartbeat to DALS registry."""
        try:
            requests.post(
                f"{API_BASE}/workers/heartbeat",
                json={"worker_name": f"{WORKER_NAME}-{self.user_id}"},
                timeout=3
            )
        except:
            pass  # Silent fail - heartbeat is non-critical

    # ---------- Core Loop ----------
    def run(self) -> None:
        """Main message processing loop - DALS manager supervises."""
        print(f"[Josephine] Starting TrueMark mint assistance...")
        while True:
            try:
                msg = self._pull_user_message()
                if msg:
                    self._handle_message(msg)
                time.sleep(0.5)
            except KeyboardInterrupt:
                print(f"[Josephine] Shutting down gracefully...")
                break
            except Exception as e:
                print(f"[Josephine] Loop error: {e}")
                time.sleep(5)

    # ---------- Messaging ----------
    def _pull_user_message(self) -> Optional[Dict[str, Any]]:
        """Pull messages from the message queue."""
        try:
            r = requests.post(
                f"{API_BASE}/host/pull",
                json={"worker_name": WORKER_NAME, "user_id": self.user_id},
                timeout=5
            )
            if r.status_code == 200 and r.json().get("text"):
                return r.json()
        except:
            pass
        return None

    def _send_reply(self, text: str, metadata: Optional[Dict] = None) -> None:
        """Send reply via TTS and/or chat."""
        # Voice output
        if TTS_URL:
            try:
                requests.post(
                    TTS_URL,
                    json={"text": text, "voice": "Josephine", "accent": "friendly"},
                    timeout=3
                )
            except Exception as e:
                print(f"[Josephine] TTS error: {e}")
        
        # Chat bubble
        if CHAT_URL:
            try:
                requests.post(
                    CHAT_URL,
                    json={
                        "user_id": self.user_id,
                        "worker": "Josephine",
                        "text": text,
                        "meta": metadata or {},
                        "avatar": "💎"
                    },
                    timeout=3
                )
            except Exception as e:
                print(f"[Josephine] Chat error: {e}")
        
        # Console fallback
        print(f"[Josephine → {self.user_id}]: {text}")

    # ---------- Dialog Router ----------
    def _handle_message(self, msg: Dict[str, Any]) -> None:
        """Route messages based on minting workflow."""
        text = msg["text"].strip().lower()
        
        # === Greeting & Introduction ===
        if any(k in text for k in ("hello", "hi", "hey", "start")):
            self._greet_user()
        
        # === Wallet Connection ===
        elif any(k in text for k in ("connect wallet", "metamask", "wallet")):
            self._handle_wallet_connection(text)
        
        # === Minting Questions ===
        elif any(k in text for k in ("what is", "explain", "how does")):
            if "truemark" in text:
                self._explain_truemark()
            elif "nft" in text or "mint" in text:
                self._explain_nft_minting()
            elif "ipfs" in text:
                self._explain_ipfs()
            elif "blockchain" in text or "certificate" in text:
                self._explain_blockchain_cert()
            else:
                self._fallback(msg)
        
        # === Mint Initiation ===
        elif any(k in text for k in ("mint", "create nft", "mint my")):
            self._initiate_mint(text)
        
        # === Mint Status ===
        elif any(k in text for k in ("status", "check mint", "where is my")):
            self._check_mint_status()
        
        # === Pricing ===
        elif any(k in text for k in ("price", "cost", "how much", "fee")):
            self._explain_pricing()
        
        # === Transaction Help ===
        elif any(k in text for k in ("stuck", "failed", "error", "problem")):
            self._troubleshoot_mint(text)
        
        # === Wallet Address ===
        elif text.startswith("0x") and len(text) == 42:
            self._save_wallet_address(text)
        
        # === Generic Help ===
        elif any(k in text for k in ("help", "guide", "how to")):
            self._provide_help()
        
        # === Fallback to SKG ===
        else:
            self._fallback(msg)

    # ---------- Greeting ----------
    def _greet_user(self):
        """Welcome message for new users."""
        self._send_reply(
            "Hi! I'm Josephine, your TrueMark NFT minting specialist. 💎\n\n"
            "I'll help you create blockchain-certified NFTs for your digital assets. "
            "TrueMark mints include:\n"
            "• Blockchain certificate with cryptographic proof\n"
            "• IPFS permanent storage\n"
            "• Signed PDF with certificate details\n\n"
            "Ready to mint your first NFT? Just say 'mint' or 'connect wallet' to begin!"
        )

    # ---------- Wallet Management ----------
    def _handle_wallet_connection(self, text: str):
        """Guide user through wallet connection."""
        if not self.mint_state["wallet_connected"]:
            self._send_reply(
                "Let's connect your Web3 wallet! 🔗\n\n"
                "I support:\n"
                "• MetaMask (recommended)\n"
                "• WalletConnect\n"
                "• Coinbase Wallet\n\n"
                "Click the 'Connect Wallet' button on the mint page, "
                "or paste your wallet address here (starts with 0x).\n\n"
                "Don't have a wallet? I can guide you through setting up MetaMask."
            )
        else:
            self._send_reply(
                f"Your wallet is already connected! ✅\n"
                f"Address: {self.mint_state['wallet_address'][:10]}...{self.mint_state['wallet_address'][-8:]}\n\n"
                "You're all set to mint NFTs!"
            )

    def _save_wallet_address(self, address: str):
        """Save and confirm wallet address."""
        self.mint_state["wallet_connected"] = True
        self.mint_state["wallet_address"] = address
        
        self._send_reply(
            f"Perfect! Wallet connected ✅\n"
            f"Address: {address[:10]}...{address[-8:]}\n\n"
            "You can now mint NFTs. Say 'mint' to create your first TrueMark certificate!"
        )

    # ---------- Explanations ----------
    def _explain_truemark(self):
        """Explain TrueMark system."""
        self._send_reply(
            "🏛️ TrueMark is a blockchain certification system that creates:\n\n"
            "1. **NFT Certificate** - Unique token proving ownership\n"
            "2. **IPFS Storage** - Permanent, decentralized file storage\n"
            "3. **Cryptographic Proof** - Tamper-proof verification\n"
            "4. **Signed PDF** - Beautiful certificate for display\n\n"
            "Unlike basic NFTs, TrueMark certificates include full metadata, "
            "creation timestamp, and legal authentication.\n\n"
            "Want to mint one? Say 'mint' to get started!"
        )

    def _explain_nft_minting(self):
        """Explain NFT minting process."""
        self._send_reply(
            "🎨 Minting an NFT means creating a unique digital certificate on the blockchain.\n\n"
            "The TrueMark process:\n"
            "1. **Upload** - Share your file (document, image, audio, etc.)\n"
            "2. **Hash** - Create cryptographic fingerprint\n"
            "3. **IPFS** - Store permanently on decentralized network\n"
            "4. **Mint** - Write certificate to blockchain\n"
            "5. **Sign** - Generate signed PDF proof\n\n"
            "Time: ~2-5 minutes\n"
            "Cost: Network gas fees (usually $5-20)\n\n"
            "Ready to try? Say 'mint my asset'!"
        )

    def _explain_ipfs(self):
        """Explain IPFS storage."""
        self._send_reply(
            "📦 IPFS (InterPlanetary File System) is permanent storage for your files.\n\n"
            "Why it's awesome:\n"
            "• **Permanent** - Files never disappear\n"
            "• **Decentralized** - No single point of failure\n"
            "• **Verifiable** - Content-addressed by hash\n"
            "• **Fast** - Distributed across nodes\n\n"
            "Your TrueMark certificate includes an IPFS hash (starts with 'Qm...' or 'bafy...').\n"
            "Anyone can verify your file using this hash forever!\n\n"
            "Questions about the tech? Just ask!"
        )

    def _explain_blockchain_cert(self):
        """Explain blockchain certificates."""
        self._send_reply(
            "🔐 Blockchain certificates are cryptographically-secured proof of ownership.\n\n"
            "Your TrueMark cert contains:\n"
            "• **Creator** - Your wallet address\n"
            "• **Timestamp** - Exact creation date/time\n"
            "• **File Hash** - Cryptographic fingerprint\n"
            "• **IPFS Link** - Permanent storage location\n"
            "• **Signature** - Tamper-proof seal\n\n"
            "This creates an immutable record that proves:\n"
            "✅ You created/owned this file\n"
            "✅ It existed at this specific time\n"
            "✅ The file hasn't been altered\n\n"
            "Perfect for copyrights, legal docs, and authenticity!"
        )

    def _explain_pricing(self):
        """Explain minting costs."""
        self._send_reply(
            "💰 TrueMark Minting Costs:\n\n"
            "**Service Fee**: FREE for GOAT users! 🎉\n"
            "**Gas Fee**: ~$5-20 (varies with network traffic)\n\n"
            "The gas fee goes to Ethereum miners, not us. "
            "I'll show you the exact cost before confirming.\n\n"
            "Pro tips:\n"
            "• Mint during off-peak hours (evenings/weekends) for lower fees\n"
            "• Batch multiple items to save on gas\n"
            "• I'll alert you if fees are unusually high\n\n"
            "Ready to proceed? Say 'mint'!"
        )

    # ---------- Minting Workflow ----------
    def _initiate_mint(self, text: str):
        """Start the minting process."""
        if not self.mint_state["wallet_connected"]:
            self._send_reply(
                "Let's connect your wallet first! 🔗\n\n"
                "Click 'Connect Wallet' or paste your wallet address (starts with 0x)."
            )
            return
        
        # Check TrueMark API status
        try:
            status_response = requests.get(f"{TRUEMARK_API}/status", timeout=3)
            if status_response.status_code != 200:
                self._send_reply(
                    "The TrueMark minting service is temporarily unavailable. "
                    "Let me escalate this to Caleon for assistance..."
                )
                self._escalate("TrueMark service unavailable")
                return
        except Exception as e:
            print(f"[Josephine] TrueMark API error: {e}")
        
        # Guide through mint
        self._send_reply(
            "Excellent! Let's mint your NFT certificate. 🚀\n\n"
            "**Step 1: Upload Your File**\n"
            "Click 'Choose File' on the mint page or drag & drop.\n"
            "Supported: PDF, JPG, PNG, MP3, MP4, TXT, DOCX\n"
            "Max size: 100 MB\n\n"
            "Once uploaded, I'll:\n"
            "1. Generate cryptographic hash\n"
            "2. Upload to IPFS\n"
            "3. Create blockchain certificate\n"
            "4. Request your signature\n\n"
            "Upload your file and I'll guide you through each step!"
        )

    def _check_mint_status(self):
        """Check status of active mints."""
        if not self.mint_state["current_mint"]:
            if self.mint_state["mint_history"]:
                last_mint = self.mint_state["mint_history"][-1]
                self._send_reply(
                    f"Your last mint:\n"
                    f"• Transaction: {last_mint.get('tx_hash', 'N/A')}\n"
                    f"• Status: {last_mint.get('status', 'Unknown')}\n"
                    f"• Time: {last_mint.get('timestamp', 'Unknown')}\n\n"
                    "Want to mint another? Say 'mint'!"
                )
            else:
                self._send_reply(
                    "You don't have any active mints yet.\n\n"
                    "Ready to create your first TrueMark NFT? Say 'mint' to begin!"
                )
        else:
            # Check with API
            mint_id = self.mint_state["current_mint"]
            self._send_reply(
                f"Checking your mint status...\n"
                f"Mint ID: {mint_id}\n\n"
                "⏳ Processing (this usually takes 2-5 minutes)\n\n"
                "I'll notify you when it's complete!"
            )

    def _troubleshoot_mint(self, text: str):
        """Help with failed or stuck transactions."""
        self._send_reply(
            "Don't worry, I can help troubleshoot! 🔧\n\n"
            "Common issues:\n\n"
            "**Transaction Failed:**\n"
            "• Check you have enough ETH for gas\n"
            "• Network might be congested (try again in 10 min)\n"
            "• Wallet might have rejected - check MetaMask\n\n"
            "**Stuck Pending:**\n"
            "• Wait 5-10 minutes (network can be slow)\n"
            "• Check Etherscan with your transaction hash\n"
            "• May need to speed up with higher gas\n\n"
            "**Upload Failed:**\n"
            "• File might be too large (max 100 MB)\n"
            "• Check internet connection\n"
            "• Try a different browser\n\n"
            "Still stuck? Share your transaction hash (starts with 0x) "
            "and I'll investigate with Caleon!"
        )

    def _provide_help(self):
        """General help menu."""
        self._send_reply(
            "🎯 **Josephine's TrueMark Help Menu**\n\n"
            "I can help you:\n\n"
            "**Getting Started:**\n"
            "• 'connect wallet' - Link your Web3 wallet\n"
            "• 'mint' - Create an NFT certificate\n"
            "• 'explain truemark' - Learn about the system\n\n"
            "**During Minting:**\n"
            "• 'status' - Check mint progress\n"
            "• 'price' - See current costs\n"
            "• 'stuck' - Troubleshoot issues\n\n"
            "**Learning:**\n"
            "• 'what is ipfs' - Understand storage\n"
            "• 'blockchain certificate' - How it works\n"
            "• 'nft' - NFT basics\n\n"
            "Or just ask me anything! I'm here to guide you through every step. 💎"
        )

    # ---------- SKG Fallback ----------
    def _fallback(self, msg: Dict[str, Any]):
        """Handle unrecognized queries with SKG or vault."""
        query = msg["text"]

        user_id_str = self.user_id if self.user_id is not None else ""
        if self.skg:
            # Try micro-SKG
            clusters = self.skg.bootstrap(query, user_id=user_id_str)

            if clusters and clusters[0]["density"] > 0.3:
                top = clusters[0]
                answer = (
                    f"Based on what I know about NFT minting:\n"
                    f"{', '.join(top['nodes'][:5])} seem related (confidence: {top['density']:.0%}).\n\n"
                    f"Could you rephrase your question? Or say 'help' for my menu!"
                )
                self._send_reply(answer, metadata=self.skg.to_pyvis_dict())
                self._feed_caleon(clusters)
                return

        # Vault and escalate
        vault_query(
            user_id_str,
            self.session_id,
            query,
            clusters_found=0,
            worker="Josephine",
            reason="no_cluster"
        )

        self._send_reply(
            "Hmm, I'm not sure about that one. Let me check with Caleon... 🤔"
        )
        self._escalate(query)

    # ---------- Integration ----------
    def _feed_caleon(self, clusters: list):
        """Send clusters to Caleon for global learning."""
        try:
            requests.post(
                f"{API_BASE}/caleon/ingest_clusters",
                json={
                    "user_id": self.user_id,
                    "worker": "Josephine",
                    "clusters": clusters,
                    "timestamp": time.time()
                },
                timeout=3
            )
        except Exception as e:
            print(f"[Josephine] Caleon feed error: {e}")

    def _escalate(self, query: str):
        """Escalate to UCM/Caleon."""
        try:
            r = requests.post(
                f"{API_BASE}/ucm/escalate",
                json={
                    "user_id": self.user_id,
                    "query": query,
                    "worker": "Josephine",
                    "context": "truemark_mint"
                },
                timeout=5
            )
            if r.status_code != 200:
                print(f"[Josephine] Escalation failed: {r.status_code}")
        except Exception as e:
            print(f"[Josephine] Escalation error: {e}")


# ---------- FastAPI Endpoints ----------
@app.post("/predicate")
async def receive_predicate(req: Request):
    """Receive new predicate from Caleon."""
    pred = await req.json()
    print(f"[Josephine] 📚 New predicate: {pred.get('name')} (confidence: {pred.get('confidence')})")
    
    # Inject into SKG if available
    if worker.skg:
        A, B = pred["signature"]
        worker.skg.G.add_edge(
            A, B,
            predicate=pred["name"],
            confidence=pred["confidence"],
            pid=pred["predicate_id"]
        )
    return {"status": "accepted"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "worker": "Josephine",
        "status": "operational",
        "user_id": worker.user_id,
        "wallet_connected": worker.mint_state["wallet_connected"],
        "active_mints": 1 if worker.mint_state["current_mint"] else 0
    }

@app.post("/mint/callback")
async def mint_callback(req: Request):
    """Receive mint status updates from TrueMark API."""
    data = await req.json()
    mint_id = data.get("mint_id")
    status = data.get("status")
    tx_hash = data.get("tx_hash")
    
    print(f"[Josephine] Mint update: {mint_id} -> {status}")
    
    if status == "completed":
        worker._send_reply(
            f"🎉 Your NFT mint is complete!\n\n"
            f"Transaction: {tx_hash}\n"
            f"View on Etherscan: https://etherscan.io/tx/{tx_hash}\n\n"
            f"Your certificate is ready! Check your wallet and IPFS link."
        )
        worker.mint_state["mint_history"].append({
            "mint_id": mint_id,
            "tx_hash": tx_hash,
            "status": status,
            "timestamp": time.time()
        })
        worker.mint_state["current_mint"] = None
    elif status == "failed":
        worker._send_reply(
            f"⚠️ Mint failed: {data.get('error', 'Unknown error')}\n\n"
            f"Don't worry! Say 'stuck' and I'll help troubleshoot."
        )
        worker.mint_state["current_mint"] = None
    
    return {"status": "received"}


# ---------- Main ----------
if __name__ == "__main__":
    if not USER_ID:
        print("ERROR: TARGET_USER_ID environment variable required")
        import sys
        sys.exit(1)
    
    # Create worker instance
    worker = JosephineTrueMarkWorker()
    
    # Run FastAPI in background
    import threading
    def run_api():
        uvicorn.run(app, host="0.0.0.0", port=WORKER_PORT, log_level="warning")
    
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    print(f"[Josephine] API running on port {WORKER_PORT}")
    
    # Run worker loop in foreground
    worker.run()
