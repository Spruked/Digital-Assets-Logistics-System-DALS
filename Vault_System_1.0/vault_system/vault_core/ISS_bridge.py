# ISS_bridge.py

"""
ISS Bridge - Inter-System Synchronization Layer

This module provides the bridge between the vault system and external
ISS (Inter-System Synchronization) networks, enabling distributed
vault synchronization and cross-system communication.
"""

import asyncio
import json
import hashlib
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import aiohttp
import websockets
from websockets.exceptions import ConnectionClosedError
import threading


class ISSMessage:
    """
    Represents a message in the ISS protocol.
    """

    def __init__(self, message_type: str, payload: Dict[str, Any],
                 source_node: str, target_node: Optional[str] = None,
                 correlation_id: Optional[str] = None, priority: str = "normal"):
        """
        Initialize an ISS message.

        Args:
            message_type: Type of message (sync, query, response, etc.)
            payload: Message payload data
            source_node: Source node identifier
            target_node: Target node identifier (None for broadcast)
            correlation_id: Correlation ID for request/response pairing
            priority: Message priority (low, normal, high, critical)
        """
        self.message_id = f"iss_{int(time.time()*1000000)}"
        self.timestamp = datetime.now()
        self.message_type = message_type
        self.payload = payload
        self.source_node = source_node
        self.target_node = target_node
        self.correlation_id = correlation_id or self.message_id
        self.priority = priority
        self.signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type,
            "payload": self.payload,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "correlation_id": self.correlation_id,
            "priority": self.priority,
            "signature": self.signature
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ISSMessage':
        """Create message from dictionary"""
        target_node = data.get("target_node")
        if target_node is not None:
            target_node = str(target_node)
        correlation_id = data.get("correlation_id")
        if correlation_id is None:
            correlation_id = data["message_id"]
        else:
            correlation_id = str(correlation_id)
        message = cls(
            message_type=data["message_type"],
            payload=data["payload"],
            source_node=data["source_node"],
            target_node=target_node,
            correlation_id=correlation_id,
            priority=data.get("priority", "normal")
        )
        message.message_id = data["message_id"]
        message.timestamp = datetime.fromisoformat(data["timestamp"])
        message.signature = data.get("signature")
        return message


class ISSConnector:
    """
    ISS Connector for distributed vault synchronization.

    Handles communication with other vault systems through the ISS protocol,
    enabling cross-system data synchronization and coordination.
    """

    def __init__(self, node_id: str, private_key_pem: str,
                 iss_network_url: str = "ws://localhost:8080/iss",
                 http_api_url: str = "http://localhost:8080/api"):
        """
        Initialize the ISS connector.

        Args:
            node_id: Unique identifier for this node
            private_key_pem: Private key for message signing
            iss_network_url: WebSocket URL for ISS network
            http_api_url: HTTP API URL for ISS services
        """
        self.node_id = node_id
        self.iss_network_url = iss_network_url
        self.http_api_url = http_api_url

        # Cryptographic keys
        try:
            self.private_key = serialization.load_pem_private_key(
                private_key_pem.encode(),
                password=None
            )
        except (ValueError, Exception):
            # Generate a new key if the provided key is invalid
            print("⚠️  Invalid private key provided, generating new key pair")
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )

        self.public_key = self.private_key.public_key()

        # Connection state
        self.websocket = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10

        # Message handling
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.response_timeout = 30  # seconds

        # Synchronization state
        self.last_sync_timestamp = None
        self.sync_peers: List[str] = []
        self.sync_handlers: List[Callable] = []

        # Background tasks
        self.running = False
        self.network_thread = None
        self.heartbeat_task = None

        # Register default handlers
        self._register_default_handlers()

        print(f"🌐 ISS Connector initialized for node {node_id}")

    def _register_default_handlers(self):
        """Register default message handlers"""
        self.register_message_handler("sync_request", self._handle_sync_request)
        self.register_message_handler("sync_response", self._handle_sync_response)
        self.register_message_handler("health_check", self._handle_health_check)
        self.register_message_handler("peer_discovery", self._handle_peer_discovery)

    async def connect(self) -> bool:
        """
        Connect to the ISS network.

        Returns:
            Connection success status
        """
        try:
            print(f"🔌 Connecting to ISS network at {self.iss_network_url}...")
            self.websocket = await websockets.connect(self.iss_network_url)
            self.connected = True
            self.reconnect_attempts = 0

            # Start background tasks
            self.running = True
            asyncio.create_task(self._heartbeat_loop())
            asyncio.create_task(self._message_loop())

            print(f"✅ Connected to ISS network as {self.node_id}")
            return True

        except Exception as e:
            print(f"❌ Failed to connect to ISS network: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from the ISS network"""
        self.running = False

        if self.websocket:
            await self.websocket.close()
            self.websocket = None

        self.connected = False
        print("🔌 Disconnected from ISS network")

    def register_message_handler(self, message_type: str, handler: Callable):
        """
        Register a handler for a specific message type.

        Args:
            message_type: Type of message to handle
            handler: Async handler function
        """
        self.message_handlers[message_type] = handler

    def register_sync_handler(self, handler: Callable):
        """
        Register a handler for synchronization events.

        Args:
            handler: Sync handler function
        """
        self.sync_handlers.append(handler)

    async def send_message(self, message: ISSMessage) -> bool:
        """
        Send a message through the ISS network.

        Args:
            message: Message to send

        Returns:
            Send success status
        """
        if not self.connected or not self.websocket:
            print("⚠️  Not connected to ISS network")
            return False

        try:
            # Sign the message
            message.signature = self._sign_message(message)

            # Send the message
            message_data = json.dumps(message.to_dict())
            await self.websocket.send(message_data)

            return True

        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False

    async def send_request(self, message_type: str, payload: Dict[str, Any],
                          target_node: Optional[str] = None, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Send a request and wait for response.

        Args:
            message_type: Type of request
            payload: Request payload
            target_node: Target node (None for broadcast)
            timeout: Response timeout in seconds

        Returns:
            Response payload or None if timeout
        """
        message = ISSMessage(
            message_type=message_type,
            payload=payload,
            source_node=self.node_id,
            target_node=target_node
        )

        # Create future for response
        future = asyncio.Future()
        self.pending_responses[message.correlation_id] = future

        # Send the request
        if not await self.send_message(message):
            del self.pending_responses[message.correlation_id]
            return None

        # Wait for response
        try:
            timeout = timeout or self.response_timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            print(f"⏰ Request timeout for correlation_id {message.correlation_id}")
            del self.pending_responses[message.correlation_id]
            return None

    def _sign_message(self, message: ISSMessage) -> str:
        """Sign a message with the private key (must be RSA)."""
        message_data = json.dumps({
            "message_id": message.message_id,
            "timestamp": message.timestamp.isoformat(),
            "message_type": message.message_type,
            "payload": message.payload,
            "source_node": message.source_node,
            "target_node": message.target_node,
            "correlation_id": message.correlation_id,
            "priority": message.priority
        }, sort_keys=True)

        # Only support RSA keys for signing
        if not hasattr(self.private_key, 'sign') or not isinstance(self.private_key, rsa.RSAPrivateKey):
            raise TypeError("Private key must be an RSA private key for signing.")

        signature = self.private_key.sign(
            message_data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature.hex()

    def _verify_message_signature(self, message: ISSMessage, public_key_pem: str) -> bool:
        """Verify message signature (only supports RSA public keys)."""
        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode())

            # Only support RSA public keys for verification
            from cryptography.hazmat.primitives.asymmetric import rsa as rsa_module
            if not isinstance(public_key, rsa_module.RSAPublicKey):
                # Not an RSA key, cannot verify
                return False

            message_data = json.dumps({
                "message_id": message.message_id,
                "timestamp": message.timestamp.isoformat(),
                "message_type": message.message_type,
                "payload": message.payload,
                "source_node": message.source_node,
                "target_node": message.target_node,
                "correlation_id": message.correlation_id,
                "priority": message.priority
            }, sort_keys=True)

            if message.signature is None:
                return False
            signature_bytes = bytes.fromhex(message.signature)

            public_key.verify(
                signature_bytes,
                message_data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return True

        except Exception:
            return False

    async def _message_loop(self):
        """Main message processing loop"""
        while self.running and self.connected:
            try:
                # Receive message
                message_data = await self.websocket.recv()
                message_dict = json.loads(message_data)
                message = ISSMessage.from_dict(message_dict)

                # Process message
                await self._process_message(message)

            except ConnectionClosedError:
                print("🔌 ISS connection closed")
                self.connected = False
                break
            except Exception as e:
                print(f"⚠️  Error processing message: {e}")
                continue

    async def _process_message(self, message: ISSMessage):
        """Process an incoming message"""
        # Check if it's a response to a pending request
        if message.correlation_id in self.pending_responses:
            future = self.pending_responses.pop(message.correlation_id)
            if not future.done():
                future.set_result(message.payload)
            return

        # Handle the message with registered handler
        if message.message_type in self.message_handlers:
            try:
                await self.message_handlers[message.message_type](message)
            except Exception as e:
                print(f"⚠️  Error in message handler for {message.message_type}: {e}")
        else:
            print(f"⚠️  No handler for message type: {message.message_type}")

    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        while self.running and self.connected:
            try:
                heartbeat = ISSMessage(
                    message_type="heartbeat",
                    payload={"status": "alive", "timestamp": datetime.now().isoformat()},
                    source_node=self.node_id
                )
                await self.send_message(heartbeat)
                await asyncio.sleep(30)  # Heartbeat every 30 seconds

            except Exception as e:
                print(f"⚠️  Heartbeat failed: {e}")
                break

    async def _handle_sync_request(self, message: ISSMessage):
        """Handle synchronization request"""
        print(f"🔄 Received sync request from {message.source_node}")

        # Prepare sync data (this would be implemented by the vault system)
        sync_data = {
            "node_id": self.node_id,
            "last_sync": self.last_sync_timestamp.isoformat() if self.last_sync_timestamp else None,
            "status": "ready"
        }

        # Send response
        response = ISSMessage(
            message_type="sync_response",
            payload=sync_data,
            source_node=self.node_id,
            target_node=message.source_node,
            correlation_id=message.correlation_id
        )

        await self.send_message(response)

        # Notify sync handlers
        for handler in self.sync_handlers:
            try:
                await handler(message.payload)
            except Exception as e:
                print(f"⚠️  Sync handler error: {e}")

    async def _handle_sync_response(self, message: ISSMessage):
        """Handle synchronization response"""
        print(f"✅ Received sync response from {message.source_node}")

        # Update sync state
        self.last_sync_timestamp = datetime.now()

        # Notify sync handlers
        for handler in self.sync_handlers:
            try:
                await handler(message.payload)
            except Exception as e:
                print(f"⚠️  Sync handler error: {e}")

    async def _handle_health_check(self, message: ISSMessage):
        """Handle health check message"""
        health_response = {
            "node_id": self.node_id,
            "status": "healthy" if self.connected else "disconnected",
            "timestamp": datetime.now().isoformat(),
            "peers": len(self.sync_peers)
        }

        response = ISSMessage(
            message_type="health_response",
            payload=health_response,
            source_node=self.node_id,
            target_node=message.source_node,
            correlation_id=message.correlation_id
        )

        await self.send_message(response)

    async def _handle_peer_discovery(self, message: ISSMessage):
        """Handle peer discovery message"""
        peer_info = message.payload

        if peer_info.get("node_id") != self.node_id:
            if peer_info["node_id"] not in self.sync_peers:
                self.sync_peers.append(peer_info["node_id"])
                print(f"👥 Discovered new peer: {peer_info['node_id']}")

        # Respond with our info
        our_info = {
            "node_id": self.node_id,
            "capabilities": ["sync", "query", "health"],
            "last_seen": datetime.now().isoformat()
        }

        response = ISSMessage(
            message_type="peer_discovery_response",
            payload=our_info,
            source_node=self.node_id,
            target_node=message.source_node,
            correlation_id=message.correlation_id
        )

        await self.send_message(response)

    async def request_sync(self, target_node: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Request synchronization with another node.

        Args:
            target_node: Target node to sync with

        Returns:
            Sync response data
        """
        sync_request = {
            "request_type": "full_sync",
            "capabilities": ["vault_data", "glyph_traces", "reflections"]
        }

        return await self.send_request("sync_request", sync_request, target_node)

    async def broadcast_health_check(self) -> List[Dict[str, Any]]:
        """
        Broadcast health check to all peers.

        Returns:
            List of health responses
        """
        health_request = {"check_type": "full_health"}

        # Send to all known peers
        responses = []
        for peer in self.sync_peers:
            response = await self.send_request("health_check", health_request, peer, timeout=10)
            if response:
                responses.append({"peer": peer, "health": response})

        return responses

    async def discover_peers(self) -> List[str]:
        """
        Discover available peers in the network.

        Returns:
            List of discovered peer IDs
        """
        discovery_request = {
            "discovery_type": "network_scan",
            "node_type": "vault_system"
        }

        # Broadcast discovery message
        message = ISSMessage(
            message_type="peer_discovery",
            payload=discovery_request,
            source_node=self.node_id
        )

        await self.send_message(message)

        # Wait a bit for responses
        await asyncio.sleep(5)

        return self.sync_peers.copy()

    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current connection status.

        Returns:
            Status information
        """
        return {
            "connected": self.connected,
            "node_id": self.node_id,
            "network_url": self.iss_network_url,
            "api_url": self.http_api_url,
            "peers": self.sync_peers,
            "last_sync": self.last_sync_timestamp.isoformat() if self.last_sync_timestamp else None,
            "reconnect_attempts": self.reconnect_attempts
        }

    async def reconnect(self) -> bool:
        """
        Attempt to reconnect to the ISS network.

        Returns:
            Reconnection success status
        """
        if self.connected:
            return True

        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print("❌ Max reconnection attempts reached")
            return False

        self.reconnect_attempts += 1
        print(f"🔄 Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")

        # Disconnect first if needed
        if self.websocket:
            await self.disconnect()

        # Wait before reconnecting
        await asyncio.sleep(min(self.reconnect_attempts * 2, 30))

        return await self.connect()

    async def query_peer(self, peer_id: str, query_type: str,
                        query_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Query a specific peer for information.

        Args:
            peer_id: Peer to query
            query_type: Type of query
            query_params: Query parameters

        Returns:
            Query response
        """
        query_payload = {
            "query_type": query_type,
            "parameters": query_params,
            "requester": self.node_id
        }

        return await self.send_request("query", query_payload, peer_id)

    def start_background_sync(self, sync_interval: int = 300):
        """
        Start background synchronization with peers.

        Args:
            sync_interval: Sync interval in seconds
        """
        async def sync_loop():
            while self.running:
                try:
                    if self.connected and self.sync_peers:
                        for peer in self.sync_peers:
                            await self.request_sync(peer)
                    await asyncio.sleep(sync_interval)
                except Exception as e:
                    print(f"⚠️  Background sync error: {e}")
                    await asyncio.sleep(60)  # Wait before retrying

        asyncio.create_task(sync_loop())
        print(f"🔄 Started background sync every {sync_interval} seconds")