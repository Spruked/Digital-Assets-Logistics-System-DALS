import { useState, useEffect } from 'react'
import Layout from '../../components/Layout'
import Link from 'next/link'

export default function WorkersDashboard() {
  const [stats, setStats] = useState({
    active_workers: 0,
    total_workers: 0,
    forge_ready: false,
    last_forge: null
  })

  const [recentWorkers, setRecentWorkers] = useState([])

  useEffect(() => {
    fetchWorkerStats()
    fetchRecentWorkers()
  }, [])

  const fetchWorkerStats = async () => {
    try {
      const response = await fetch('/api/workers/status')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to fetch worker stats:', error)
    }
  }

  const fetchRecentWorkers = async () => {
    try {
      const response = await fetch('/api/workers/')
      if (response.ok) {
        const workers = await response.json()
        setRecentWorkers(workers.slice(0, 5)) // Show last 5 workers
      }
    } catch (error) {
      console.error('Failed to fetch workers:', error)
    }
  }

  const popOutWindow = (url, title, width = 1400, height = 900) => {
    const features = `width=${width},height=${height},scrollbars=yes,resizable=yes,status=yes`
    window.open(url, title, features)
  }

  return (
    <Layout title="DALS Workers Dashboard">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">⚙️ DALS Workers Control Center</h1>
          <p className="text-gray-400">Industrial-grade worker cloning and management system v2.0</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Active Workers</p>
                <p className="text-2xl font-bold text-green-400">{stats.active_workers}</p>
              </div>
              <div className="text-green-400 text-3xl">●</div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Workers</p>
                <p className="text-2xl font-bold text-blue-400">{stats.total_workers}</p>
              </div>
              <div className="text-blue-400 text-3xl">📊</div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Forge Engine</p>
                <p className="text-2xl font-bold text-purple-400">
                  {stats.forge_ready ? 'Ready' : 'Busy'}
                </p>
              </div>
              <div className="text-purple-400 text-3xl">⚒️</div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Last Forge</p>
                <p className="text-2xl font-bold text-orange-400">
                  {stats.last_forge ? new Date(stats.last_forge).toLocaleTimeString() : 'Never'}
                </p>
              </div>
              <div className="text-orange-400 text-3xl">🕐</div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Link href="/workers/registry">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-blue-500 cursor-pointer transition-colors">
              <div className="text-center">
                <div className="text-4xl mb-4">📋</div>
                <h3 className="text-lg font-semibold text-white mb-2">Worker Registry</h3>
                <p className="text-gray-400 text-sm">View and manage all workers</p>
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    popOutWindow('/workers/registry', 'Worker Registry')
                  }}
                  className="mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors"
                >
                  Pop Out →
                </button>
              </div>
            </div>
          </Link>

          <Link href="/workers/forge">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-green-500 cursor-pointer transition-colors">
              <div className="text-center">
                <div className="text-4xl mb-4">⚒️</div>
                <h3 className="text-lg font-semibold text-white mb-2">Worker Forge</h3>
                <p className="text-gray-400 text-sm">Create new workers</p>
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    popOutWindow('/workers/forge', 'Worker Forge', 1200, 800)
                  }}
                  className="mt-3 px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm transition-colors"
                >
                  Pop Out →
                </button>
              </div>
            </div>
          </Link>

          <Link href="/workers/templates">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-purple-500 cursor-pointer transition-colors">
              <div className="text-center">
                <div className="text-4xl mb-4">📄</div>
                <h3 className="text-lg font-semibold text-white mb-2">Templates</h3>
                <p className="text-gray-400 text-sm">Manage worker blueprints</p>
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    popOutWindow('/workers/templates', 'Worker Templates', 1000, 700)
                  }}
                  className="mt-3 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm transition-colors"
                >
                  Pop Out →
                </button>
              </div>
            </div>
          </Link>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="text-center">
              <div className="text-4xl mb-4">🔍</div>
              <h3 className="text-lg font-semibold text-white mb-2">Inspector</h3>
              <p className="text-gray-400 text-sm">Deep worker inspection</p>
              <button
                onClick={() => popOutWindow('/workers/inspector', 'Worker Inspector', 1300, 900)}
                className="mt-3 px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded text-sm transition-colors"
              >
                Pop Out →
              </button>
            </div>
          </div>
        </div>

        {/* Recent Workers */}
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-xl font-semibold text-white">Recent Workers</h2>
          </div>
          <div className="p-6">
            {recentWorkers.length === 0 ? (
              <div className="text-center text-gray-400 py-8">
                <div className="text-4xl mb-4">📋</div>
                <p>No workers found. Create your first worker!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {recentWorkers.map((worker) => (
                  <div key={worker.serial} className="flex items-center justify-between bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center space-x-4">
                      <div className={`w-3 h-3 rounded-full ${
                        worker.status === 'active' ? 'bg-green-400' : 'bg-yellow-400'
                      }`}></div>
                      <div>
                        <h3 className="text-white font-medium">{worker.name}</h3>
                        <p className="text-gray-400 text-sm">{worker.serial}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-400 text-sm">
                        {new Date(worker.created_at).toLocaleDateString()}
                      </span>
                      <Link href={`/workers/${worker.serial}`}>
                        <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors">
                          Inspect
                        </button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Multi-Monitor Instructions */}
        <div className="mt-8 bg-blue-900/20 border border-blue-500/30 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-400 mb-4">🖥️ Multi-Monitor Setup</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-300">
            <div>
              <h4 className="font-medium text-white mb-2">Monitor 1: Registry</h4>
              <p>Keep the main worker list and heartbeats visible at all times.</p>
            </div>
            <div>
              <h4 className="font-medium text-white mb-2">Monitor 2: Forge + Inspector</h4>
              <p>Create new workers and inspect running instances.</p>
            </div>
            <div>
              <h4 className="font-medium text-white mb-2">Monitor 3: Templates + Logs</h4>
              <p>Manage blueprints and monitor system activity.</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}