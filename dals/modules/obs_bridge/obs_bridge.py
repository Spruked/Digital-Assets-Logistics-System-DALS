# obs_bridge/obs_bridge.py
# OBS Bridge for DALS - Controls OBS Studio via WebSocket and system commands

import asyncio
import logging
import subprocess
import time
import psutil
import os
from typing import Optional, Dict, Any, List
from obswebsocket import obsws, requests, events

logger = logging.getLogger("DALS.OBSBridge")

class OBSBridge:
    """
    Bridge to control OBS Studio via WebSocket API.
    Provides methods for streaming, recording, scene switching, etc.
    """

    def __init__(self, host: str = "localhost", port: int = 4455, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.password = password
        self.obs_path = self._find_obs_executable()
        self.ws: Optional[obsws] = None
        self.connected = False
        self.obs_process: Optional[subprocess.Popen] = None
        self.current_scene: Optional[str] = None
        self.available_scenes: List[str] = []
        
        # Platform profiles
        self.platform_profiles = self._load_default_platforms()
        self.current_platform: Optional[str] = None

    def _is_obs_running(self) -> bool:
        """Check if OBS Studio is already running."""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'obs64' in proc.info['name'].lower():
                    return True
        except ImportError:
            # Fallback if psutil not available
            pass
        except Exception as e:
            logger.warning(f"Error checking for OBS processes: {e}")
        
        return False

    def _find_obs_executable(self) -> Optional[str]:
        """Find OBS executable path on the system."""
        # Common paths for OBS Studio
        common_paths = [
            "C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe",
            "C:\\Program Files (x86)\\obs-studio\\bin\\64bit\\obs64.exe",
            "/usr/bin/obs",
            "/usr/local/bin/obs",
            "/opt/obs-studio/bin/obs"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        # OBS is external service, so don't fail if not found
        logger.warning("OBS Studio executable not found. OBS Bridge will operate in external mode.")
        return None

    async def connect(self) -> bool:
        """Connect to OBS WebSocket."""
        try:
            self.ws = obsws(host=self.host, port=self.port, password=self.password or "")
            self.ws.connect()
            self.connected = True
            logger.info(f"Connected to OBS at {self.host}:{self.port}")
            await self._update_status()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to OBS: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from OBS."""
        if self.ws:
            self.ws.disconnect()
            self.connected = False
            logger.info("Disconnected from OBS")

    async def start_obs_service(self) -> bool:
        """Start OBS Studio as a system service."""
        # Check if we already have a process running
        if self.obs_process and self.obs_process.poll() is None:
            logger.info("OBS is already running (managed by DALS)")
            return True
        
        # Check if OBS is already running (manually or by other means)
        if self._is_obs_running():
            logger.info("OBS is already running (external process)")
            # Try to connect to existing instance
            return await self.wait_for_obs_ready(timeout=10)
        
        # If OBS path not found, assume external OBS
        if not self.obs_path:
            logger.warning("OBS executable not found. Please start OBS Studio manually with WebSocket enabled on port 4455.")
            # Try to connect to external OBS instance
            return await self.wait_for_obs_ready(timeout=10)
        
        try:
            # Launch OBS with WebSocket enabled
            cmd = [self.obs_path, "--websocket", "--websocket_port", str(self.port), "--minimize-to-tray"]
            if self.password:
                cmd.extend(["--websocket_password", self.password])
            
            # Set working directory to OBS installation directory for locale files
            obs_dir = os.path.dirname(os.path.dirname(os.path.dirname(self.obs_path)))
            
            # Set environment to ensure OBS can find its files
            env = os.environ.copy()
            env['OBS_DATA_PATH'] = os.path.join(obs_dir, 'data')
            
            self.obs_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                cwd=obs_dir,  # Set working directory to OBS installation root
                env=env
            )
            logger.info(f"Started OBS process: {self.obs_process.pid} in directory: {obs_dir}")
            
            # Wait a bit for OBS to initialize
            await asyncio.sleep(2)
            
            # Check if process is still running
            if self.obs_process.poll() is not None:
                # Process exited, get error output
                stdout, stderr = self.obs_process.communicate()
                stdout_str = stdout.decode('utf-8', errors='ignore') if stdout else ""
                stderr_str = stderr.decode('utf-8', errors='ignore') if stderr else ""
                logger.error(f"OBS process exited immediately. STDOUT: {stdout_str}")
                logger.error(f"OBS process exited immediately. STDERR: {stderr_str}")
                return False
            
            # Wait for OBS to be ready
            return await self.wait_for_obs_ready()
            
        except Exception as e:
            logger.error(f"Failed to start OBS service: {e}")
            return False

    async def wait_for_obs_ready(self, timeout: int = 30) -> bool:
        """Wait for OBS WebSocket to become available."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Try to connect to WebSocket
                test_ws = obsws(host=self.host, port=self.port, password=self.password or "")
                test_ws.connect()
                test_ws.disconnect()
                logger.info("OBS WebSocket is ready")
                return True
            except Exception:
                await asyncio.sleep(1)
        
        logger.error("OBS WebSocket did not become ready within timeout")
        return False

    async def stop_obs_service(self) -> bool:
        """Stop OBS Studio service cleanly."""
        if not self.obs_process:
            logger.info("No OBS process to stop")
            return True
        
        try:
            # First try graceful shutdown via WebSocket
            if self.connected and self.ws:
                try:
                    self.ws.call(requests.StopStreaming())
                    self.ws.call(requests.StopRecording())
                    # Note: OBS WebSocket doesn't have a direct quit command
                    # We'll rely on process termination
                except Exception as e:
                    logger.warning(f"Failed to stop streaming/recording gracefully: {e}")
            
            # Terminate the process
            self.obs_process.terminate()
            
            # Wait for process to exit
            try:
                self.obs_process.wait(timeout=10)
                logger.info("OBS process terminated gracefully")
            except subprocess.TimeoutExpired:
                logger.warning("OBS process did not terminate gracefully, killing...")
                self.obs_process.kill()
                self.obs_process.wait()
                logger.info("OBS process killed")
            
            self.obs_process = None
            self.connected = False
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop OBS service: {e}")
            return False

    async def kill_obs_process(self) -> bool:
        """Force kill any running OBS processes."""
        killed = False
        for proc in psutil.process_iter(['pid', 'name']):
            if 'obs' in proc.info['name'].lower():
                try:
                    psutil.Process(proc.info['pid']).kill()
                    logger.info(f"Killed OBS process: {proc.info['pid']}")
                    killed = True
                except Exception as e:
                    logger.error(f"Failed to kill OBS process {proc.info['pid']}: {e}")
        
        if killed:
            self.obs_process = None
            self.connected = False
        
        return killed

    async def _update_status(self):
        """Update current status from OBS."""
        if not self.connected or not self.ws:
            return

        try:
            # Get current scene
            scene_response = self.ws.call(requests.GetCurrentScene())
            self.current_scene = scene_response.getSceneName()

            # Get available scenes
            scenes_response = self.ws.call(requests.GetSceneList())
            self.available_scenes = [scene['name'] for scene in scenes_response.getScenes()]

        except Exception as e:
            logger.error(f"Failed to update OBS status: {e}")

    async def start_stream(self) -> bool:
        """Start streaming."""
        if not self.connected or not self.ws:
            return False
        try:
            self.ws.call(requests.StartStreaming())
            logger.info("Started OBS streaming")
            return True
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            return False

    async def stop_stream(self) -> bool:
        """Stop streaming."""
        if not self.connected or not self.ws:
            return False
        try:
            self.ws.call(requests.StopStreaming())
            logger.info("Stopped OBS streaming")
            return True
        except Exception as e:
            logger.error(f"Failed to stop streaming: {e}")
            return False

    async def start_recording(self) -> bool:
        """Start recording."""
        if not self.connected or not self.ws:
            return False
        try:
            self.ws.call(requests.StartRecording())
            logger.info("Started OBS recording")
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False

    async def stop_recording(self) -> bool:
        """Stop recording."""
        if not self.connected or not self.ws:
            return False
        try:
            self.ws.call(requests.StopRecording())
            logger.info("Stopped OBS recording")
            return True
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return False

    async def switch_scene(self, scene_name: str) -> bool:
        """Switch to a specific scene."""
        if not self.connected or not self.ws:
            return False
        try:
            self.ws.call(requests.SetCurrentScene(scene_name))
            self.current_scene = scene_name
            logger.info(f"Switched to scene: {scene_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to scene {scene_name}: {e}")
            return False

    async def get_status(self) -> Dict[str, Any]:
        """Get current OBS status."""
        await self._update_status()
        process_running = self.obs_process and self.obs_process.poll() is None
        
        return {
            "connected": self.connected,
            "process_running": process_running,
            "streaming": self._is_streaming(),
            "recording": self._is_recording(),
            "current_scene": self.current_scene,
            "available_scenes": self.available_scenes,
            "health": "healthy" if self.connected else "disconnected"
        }

    def _is_streaming(self) -> bool:
        """Check if currently streaming."""
        if not self.connected or not self.ws:
            return False
        try:
            response = self.ws.call(requests.GetStreamingStatus())
            return response.getStreaming()
        except:
            return False

    def _is_recording(self) -> bool:
        """Check if currently recording."""
        if not self.connected or not self.ws:
            return False
        try:
            response = self.ws.call(requests.GetRecordingStatus())
            return response.getIsRecording()
        except:
            return False

    def _load_default_platforms(self) -> Dict[str, Dict[str, Any]]:
        """Load default platform RTMP profiles."""
        return {
            "tiktok": {
                "name": "TikTok Live",
                "platform": "tiktok",
                "rtmp_url": "rtmp://live.tiktok.com/live/",
                "description": "TikTok Live Streaming"
            },
            "youtube": {
                "name": "YouTube Live",
                "platform": "youtube", 
                "rtmp_url": "rtmp://a.rtmp.youtube.com/live2/",
                "description": "YouTube Live Streaming"
            },
            "facebook": {
                "name": "Facebook Live",
                "platform": "facebook",
                "rtmp_url": "rtmp://rtmp-api.facebook.com:80/rtmp/",
                "description": "Facebook Live Streaming"
            },
            "twitch": {
                "name": "Twitch",
                "platform": "twitch",
                "rtmp_url": "rtmp://live.twitch.tv/app/",
                "description": "Twitch Live Streaming"
            },
            "custom": {
                "name": "Custom RTMP",
                "platform": "custom",
                "rtmp_url": "",
                "description": "Custom RTMP Server"
            }
        }

    def get_platform_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all available platform profiles."""
        return self.platform_profiles

    def get_current_platform(self) -> Optional[str]:
        """Get currently selected platform."""
        return self.current_platform

    async def set_platform_profile(self, platform: str, stream_key: Optional[str] = None) -> bool:
        """Set OBS stream settings for the selected platform."""
        if not self.connected or not self.ws:
            logger.error("Not connected to OBS")
            return False

        if platform not in self.platform_profiles:
            logger.error(f"Unknown platform: {platform}")
            return False

        profile = self.platform_profiles[platform]
        rtmp_url = profile["rtmp_url"]

        # For platforms that need a stream key, append it to the URL
        if stream_key and platform != "custom":
            rtmp_url = f"{rtmp_url}{stream_key}"

        try:
            # Set stream settings in OBS
            stream_settings = {
                "server": rtmp_url,
                "key": stream_key or "",
                "use_auth": False
            }

            self.ws.call(requests.SetStreamSettings(
                type="rtmp_custom",
                settings=stream_settings,
                save=True
            ))

            self.current_platform = platform
            logger.info(f"Set OBS stream settings for platform: {platform}")
            return True

        except Exception as e:
            logger.error(f"Failed to set platform profile {platform}: {e}")
            return False

    # Additional methods can be added for overlays, transitions, etc.
    # For now, focus on core functionality