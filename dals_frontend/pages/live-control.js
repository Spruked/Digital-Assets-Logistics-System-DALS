import { useState, useEffect } from 'react'
import Layout from '../../components/Layout'

export default function LiveControlPanel() {
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
    loadOBSStatus()
    loadScenes()
  }, [])

  const loadOBSStatus = async () => {
    try {
      const response = await fetch('/api/obs/status')
      if (response.ok) {
        const status = await response.json()
        setObsStatus(status)
      }
    } catch (error) {
      console.error('Failed to load OBS status:', error)
    }
  }

  const loadScenes = async () => {
    try {
      const response = await fetch('/api/obs/scenes')
      if (response.ok) {
        const sceneData = await response.json()
        setScenes(sceneData.scenes || [])
      }
    } catch (error) {
      console.error('Failed to load scenes:', error)
    }
  }

  const connectToOBS = async () => {
    try {
      const response = await fetch('/api/obs/connect', { method: 'POST' })
      if (response.ok) {
        await loadOBSStatus()
      }
    } catch (error) {
      console.error('Failed to connect to OBS:', error)
    }
  }

  const disconnectFromOBS = async () => {
    try {
      const response = await fetch('/api/obs/disconnect', { method: 'POST' })
      if (response.ok) {
        await loadOBSStatus()
      }
    } catch (error) {
      console.error('Failed to disconnect from OBS:', error)
    }
  }

  const startStream = async () => {
    try {
      const response = await fetch('/api/obs/stream/start', { method: 'POST' })
      if (response.ok) {
        await loadOBSStatus()
      }
    } catch (error) {
      console.error('Failed to start stream:', error)
    }
  }

  const stopStream = async () => {
    try {
      const response = await fetch('/api/obs/stream/stop', { method: 'POST' })
      if (response.ok) {
        await loadOBSStatus()
      }
    } catch (error) {
      console.error('Failed to stop stream:', error)
    }
  }

  const startRecording = async () => {
    try {
      const response = await fetch('/api/obs/recording/start', { method: 'POST' })
      if (response.ok) {
        await loadOBSStatus()
      }
    } catch (error) {
      console.error('Failed to start recording:', error)
    }
  }

  const stopRecording = async () => {
    try {
      const response = await fetch('/api/obs/recording/stop', { method: 'POST' })
      if (response.ok) {
        await loadOBSStatus()
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
        await loadOBSStatus()
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
    // Refresh platform status logic
    setPlatformConfig(prev => ({ ...prev, status: 'Status refreshed' }))
  }

  const popOutPanel = (panelType, title, width = 600, height = 400) => {
    const params = new URLSearchParams({
      panel: panelType,
      title: title
    })
    const features = `width=${width},height=${height},scrollbars=no,resizable=yes,status=no`
    window.open(`/live-control/popout?${params}`, `popout-${panelType}`, features)
  }

  return (
    <Layout title="Live Control Panel">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">🎥 Live Control Panel</h1>
          <p className="text-gray-400">OBS Studio and Live Streaming Control Center</p>
        </div>

        {/* OBS Service Control */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center justify-between">
            ⚙️ OBS Service Control
            <button
              onClick={() => popOutPanel('obs-service', 'OBS Service Control')}
              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors"
            >
              Pop Out →
            </button>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
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

        {/* Live Platform Control */}
        <div className="bg-gray-800 rounded-lg p-6 border border-orange-500/30 mb-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center justify-between">
            🌐 Live Platform Control
            <button
              onClick={() => popOutPanel('platform', 'Live Platform Control', 500, 300)}
              className="px-3 py-1 bg-orange-600 hover:bg-orange-700 rounded text-sm transition-colors"
            >
              Pop Out →
            </button>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
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

          <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded text-sm text-gray-300">
            <strong>💡 Tip:</strong> Select a platform and click "Load Platform" to configure OBS with the correct RTMP settings.
          </div>
        </div>

        {/* Streaming Control */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center justify-between">
            📺 Streaming Control
            <button
              onClick={() => popOutPanel('streaming', 'Streaming Control', 400, 200)}
              className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm transition-colors"
            >
              Pop Out →
            </button>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
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

        {/* Scene Control */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center justify-between">
            🎬 Scene Control
            <button
              onClick={() => popOutPanel('scenes', 'Scene Control', 400, 300)}
              className="px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded text-sm transition-colors"
            >
              Pop Out →
            </button>
          </h2>

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

        {/* Status Refresh */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4">🔄 Status & Refresh</h2>
          <button
            onClick={loadOBSStatus}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded transition-colors"
          >
            ↻ Refresh OBS Status
          </button>

          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Last Update:</span>
              <span className="text-gray-500">
                {obsStatus.lastUpdate ? new Date(obsStatus.lastUpdate).toLocaleTimeString() : 'Never'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}