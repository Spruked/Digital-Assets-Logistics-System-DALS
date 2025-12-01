import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'

export default function PopoutPanel() {
  const router = useRouter()
  const { panel, title } = router.query

  const [obsStatus, setObsStatus] = useState({
    connected: false,
    streaming: false,
    recording: false,
    currentScene: 'None',
    lastUpdate: null
  })

  const [platformConfig, setPlatformConfig] = useState({
    selectedPlatform: '',
    streamKey: '',
    status: 'No platform loaded'
  })

  const [scenes, setScenes] = useState([])

  useEffect(() => {
    if (panel) {
      loadData()
      // Auto-refresh every 5 seconds
      const interval = setInterval(loadData, 5000)
      return () => clearInterval(interval)
    }
  }, [panel])

  const loadData = async () => {
    try {
      if (panel === 'obs-service' || panel === 'streaming' || panel === 'scenes') {
        const response = await fetch('/api/obs/status')
        if (response.ok) {
          const status = await response.json()
          setObsStatus(status)
        }
      }

      if (panel === 'scenes') {
        const response = await fetch('/api/obs/scenes')
        if (response.ok) {
          const sceneData = await response.json()
          setScenes(sceneData.scenes || [])
        }
      }
    } catch (error) {
      console.error('Failed to load data:', error)
    }
  }

  const connectToOBS = async () => {
    try {
      const response = await fetch('/api/obs/connect', { method: 'POST' })
      if (response.ok) {
        await loadData()
      }
    } catch (error) {
      console.error('Failed to connect to OBS:', error)
    }
  }

  const disconnectFromOBS = async () => {
    try {
      const response = await fetch('/api/obs/disconnect', { method: 'POST' })
      if (response.ok) {
        await loadData()
      }
    } catch (error) {
      console.error('Failed to disconnect from OBS:', error)
    }
  }

  const startStream = async () => {
    try {
      const response = await fetch('/api/obs/stream/start', { method: 'POST' })
      if (response.ok) {
        await loadData()
      }
    } catch (error) {
      console.error('Failed to start stream:', error)
    }
  }

  const stopStream = async () => {
    try {
      const response = await fetch('/api/obs/stream/stop', { method: 'POST' })
      if (response.ok) {
        await loadData()
      }
    } catch (error) {
      console.error('Failed to stop stream:', error)
    }
  }

  const startRecording = async () => {
    try {
      const response = await fetch('/api/obs/recording/start', { method: 'POST' })
      if (response.ok) {
        await loadData()
      }
    } catch (error) {
      console.error('Failed to start recording:', error)
    }
  }

  const stopRecording = async () => {
    try {
      const response = await fetch('/api/obs/recording/stop', { method: 'POST' })
      if (response.ok) {
        await loadData()
      }
    } catch (error) {
      console.error('Failed to stop recording:', error)
    }
  }

  const switchScene = async (sceneName) => {
    try {
      const response = await fetch('/api/obs/scene', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scene: sceneName })
      })
      if (response.ok) {
        await loadData()
      }
    } catch (error) {
      console.error('Failed to switch scene:', error)
    }
  }

  const loadPlatformProfile = async () => {
    if (!platformConfig.selectedPlatform) return

    try {
      const response = await fetch('/api/platforms/load', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform: platformConfig.selectedPlatform,
          streamKey: platformConfig.streamKey
        })
      })
      if (response.ok) {
        setPlatformConfig(prev => ({ ...prev, status: 'Platform loaded successfully' }))
      }
    } catch (error) {
      console.error('Failed to load platform:', error)
      setPlatformConfig(prev => ({ ...prev, status: 'Failed to load platform' }))
    }
  }

  const refreshPlatformStatus = () => {
    setPlatformConfig(prev => ({ ...prev, status: 'Status refreshed' }))
  }

  if (!panel) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading panel...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6 text-center">{title || 'Pop-out Panel'}</h1>

        {/* OBS Service Control Panel */}
        {panel === 'obs-service' && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold text-white mb-4">⚙️ OBS Service Control</h2>

            <div className="grid grid-cols-1 gap-4 mb-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">OBS Connection:</span>
                <span className={`font-semibold ${obsStatus.connected ? 'text-green-400' : 'text-red-400'}`}>
                  {obsStatus.connected ? '● Connected' : '● Disconnected'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Last Update:</span>
                <span className="text-gray-400 text-sm">
                  {obsStatus.lastUpdate ? new Date(obsStatus.lastUpdate).toLocaleTimeString() : 'Never'}
                </span>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={connectToOBS}
                disabled={obsStatus.connected}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded transition-colors"
              >
                🔗 Connect
              </button>
              <button
                onClick={disconnectFromOBS}
                disabled={!obsStatus.connected}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded transition-colors"
              >
                🔌 Disconnect
              </button>
            </div>
          </div>
        )}

        {/* Platform Control Panel */}
        {panel === 'platform' && (
          <div className="bg-gray-800 rounded-lg p-6 border border-orange-500/30">
            <h2 className="text-xl font-semibold text-white mb-4">🌐 Live Platform Control</h2>

            <div className="grid grid-cols-1 gap-4 mb-4">
              <div>
                <label className="block text-gray-300 text-sm mb-2">Select Platform:</label>
                <select
                  value={platformConfig.selectedPlatform}
                  onChange={(e) => setPlatformConfig(prev => ({ ...prev, selectedPlatform: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                >
                  <option value="">Choose Platform...</option>
                  <option value="tiktok">🎵 TikTok</option>
                  <option value="youtube">📺 YouTube</option>
                  <option value="facebook">👥 Facebook</option>
                  <option value="twitch">🎮 Twitch</option>
                  <option value="custom">🔧 Custom RTMP</option>
                </select>
              </div>
              <div>
                <label className="block text-gray-300 text-sm mb-2">Stream Key:</label>
                <input
                  type="password"
                  value={platformConfig.streamKey}
                  onChange={(e) => setPlatformConfig(prev => ({ ...prev, streamKey: e.target.value }))}
                  placeholder="Enter stream key (optional)"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                />
              </div>
            </div>

            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-300">Status:</span>
              <span className="text-gray-400">{platformConfig.status}</span>
            </div>

            <div className="flex gap-2">
              <button
                onClick={loadPlatformProfile}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors"
              >
                📡 Load Platform
              </button>
              <button
                onClick={refreshPlatformStatus}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded transition-colors"
              >
                🔄 Refresh Status
              </button>
            </div>
          </div>
        )}

        {/* Streaming Control Panel */}
        {panel === 'streaming' && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold text-white mb-4">📺 Streaming Control</h2>

            <div className="grid grid-cols-1 gap-4 mb-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Streaming Status:</span>
                <span className={`font-semibold ${obsStatus.streaming ? 'text-green-400' : 'text-red-400'}`}>
                  {obsStatus.streaming ? '● Live' : '● Stopped'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Recording Status:</span>
                <span className={`font-semibold ${obsStatus.recording ? 'text-red-400' : 'text-gray-400'}`}>
                  {obsStatus.recording ? '● Recording' : '● Stopped'}
                </span>
              </div>
            </div>

            <div className="flex gap-2 flex-wrap">
              <button
                onClick={startStream}
                disabled={obsStatus.streaming}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded transition-colors"
              >
                ▶️ Start Stream
              </button>
              <button
                onClick={stopStream}
                disabled={!obsStatus.streaming}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded transition-colors"
              >
                ⏹️ Stop Stream
              </button>
              <button
                onClick={startRecording}
                disabled={obsStatus.recording}
                className="px-4 py-2 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 rounded transition-colors"
              >
                ⏺️ Start Recording
              </button>
              <button
                onClick={stopRecording}
                disabled={!obsStatus.recording}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded transition-colors"
              >
                ⏹️ Stop Recording
              </button>
            </div>
          </div>
        )}

        {/* Scene Control Panel */}
        {panel === 'scenes' && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold text-white mb-4">🎬 Scene Control</h2>

            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-300">Current Scene:</span>
                <span className="text-white font-semibold">{obsStatus.currentScene}</span>
              </div>
            </div>

            <div>
              <select
                onChange={(e) => switchScene(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white mb-3"
              >
                <option value="">Select Scene...</option>
                {scenes.map((scene) => (
                  <option key={scene.name} value={scene.name}>
                    {scene.name}
                  </option>
                ))}
              </select>
              <button
                onClick={() => switchScene(document.querySelector('select').value)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors"
              >
                🔄 Switch Scene
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}