import { useState, useEffect } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useRouter } from 'next/router'

export default function Layout({ children, title = "DALS Workers Control Center" }) {
  const [isFullscreen, setIsFullscreen] = useState(false)
  const router = useRouter()

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  const popOutWindow = (url, title, width = 1600, height = 1000) => {
    const features = `width=${width},height=${height},scrollbars=yes,resizable=yes,status=yes`
    window.open(url, title, features)
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Head>
        <title>{title} - DALS</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Multi-Monitor Control Bar */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-blue-400">⚙️ DALS Workers</h1>
          <div className="text-sm text-gray-400">
            Multi-Monitor Control Center
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Pop-out buttons for multi-monitor */}
          <button
            onClick={() => popOutWindow('/workers/registry', 'Workers Registry', 1400, 900)}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors"
            title="Open Registry in new window"
          >
            📋 Registry
          </button>
          <button
            onClick={() => popOutWindow('/workers/forge', 'Worker Forge', 1200, 800)}
            className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm transition-colors"
            title="Open Forge in new window"
          >
            ⚒️ Forge
          </button>
          <button
            onClick={() => popOutWindow('/workers/templates', 'Worker Templates', 1000, 700)}
            className="px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded text-sm transition-colors"
            title="Open Templates in new window"
          >
            📄 Templates
          </button>
          <button
            onClick={() => popOutWindow('/live-control', 'Live Control Panel', 1600, 1000)}
            className="px-3 py-1 bg-orange-600 hover:bg-orange-700 rounded text-sm transition-colors"
            title="Open Live Control in new window"
          >
            🎥 Live Control
          </button>

          {/* Fullscreen toggle */}
          <button
            onClick={toggleFullscreen}
            className="px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded text-sm transition-colors"
            title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
          >
            {isFullscreen ? '🗗' : '🗖'}
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            <Link href="/workers" className={`py-4 px-1 border-b-2 font-medium text-sm ${
              router.pathname === '/workers' ? 'border-blue-400 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'
            }`}>
              Dashboard
            </Link>
            <Link href="/workers/registry" className={`py-4 px-1 border-b-2 font-medium text-sm ${
              router.pathname === '/workers/registry' ? 'border-blue-400 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'
            }`}>
              Registry
            </Link>
            <Link href="/workers/forge" className={`py-4 px-1 border-b-2 font-medium text-sm ${
              router.pathname === '/workers/forge' ? 'border-blue-400 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'
            }`}>
              Forge
            </Link>
            <Link href="/live-control" className={`py-4 px-1 border-b-2 font-medium text-sm ${
              router.pathname === '/live-control' ? 'border-blue-400 text-blue-400' : 'border-transparent text-gray-400 hover:text-white'
            }`}>
              Live Control
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Status Bar */}
      <div className="bg-gray-800 border-t border-gray-700 px-4 py-2 text-xs text-gray-400">
        <div className="flex justify-between items-center">
          <div>DALS Workers Control Center v2.0</div>
          <div className="flex items-center space-x-4">
            <span>🔗 API: Connected</span>
            <span>⚡ Workers: 1 Active</span>
            <span>🖥️ Multi-Monitor: Ready</span>
          </div>
        </div>
      </div>
    </div>
  )
}