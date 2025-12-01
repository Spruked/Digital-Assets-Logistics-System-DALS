import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'

export default function WorkerInspector() {
  const router = useRouter()
  const { serial } = router.query
  const [worker, setWorker] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (serial) {
      fetchWorkerDetails()
    }
  }, [serial])

  const fetchWorkerDetails = async () => {
    try {
      const response = await fetch(`/api/workers/${serial}`)
      if (!response.ok) {
        throw new Error(`Failed to fetch worker: ${response.status}`)
      }
      const data = await response.json()
      setWorker(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'status-online'
      case 'inactive': return 'status-offline'
      case 'warning': return 'status-warning'
      default: return 'status-info'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading worker details...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 mb-4">Error: {error}</div>
          <Link href="/workers" className="btn-secondary">
            Back to Registry
          </Link>
        </div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Worker Inspector - {serial} | DALS Workers Control Center</title>
        <meta name="description" content={`Detailed inspection of worker ${serial}`} />
      </Head>

      <div className="min-h-screen bg-gray-900">
        {/* Header */}
        <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/workers" className="text-gray-400 hover:text-white">
                ← Back to Registry
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-white">Worker Inspector</h1>
                <p className="text-gray-400">Serial: {serial}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(worker?.status)}`}>
                {worker?.status || 'Unknown'}
              </span>
              <button
                onClick={() => window.location.reload()}
                className="btn-secondary"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Basic Information */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-white">Basic Information</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="form-label">Serial Number</label>
                  <p className="text-white font-mono">{worker?.serial || 'N/A'}</p>
                </div>
                <div>
                  <label className="form-label">Template</label>
                  <p className="text-white">{worker?.template || 'N/A'}</p>
                </div>
                <div>
                  <label className="form-label">Created</label>
                  <p className="text-white">{worker?.created_at || 'Never'}</p>
                </div>
                <div>
                  <label className="form-label">Last Active</label>
                  <p className="text-white">{worker?.last_active || 'Never'}</p>
                </div>
                <div>
                  <label className="form-label">Uptime</label>
                  <p className="text-white">{worker?.uptime || '0 seconds'}</p>
                </div>
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-white">Performance Metrics</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="form-label">Tasks Completed</label>
                  <p className="text-white text-2xl font-bold">{worker?.tasks_completed || 0}</p>
                </div>
                <div>
                  <label className="form-label">Success Rate</label>
                  <p className="text-white text-2xl font-bold">{worker?.success_rate || '0%'}</p>
                </div>
                <div>
                  <label className="form-label">Average Response Time</label>
                  <p className="text-white">{worker?.avg_response_time || 'N/A'}</p>
                </div>
                <div>
                  <label className="form-label">Memory Usage</label>
                  <p className="text-white">{worker?.memory_usage || 'N/A'}</p>
                </div>
                <div>
                  <label className="form-label">CPU Usage</label>
                  <p className="text-white">{worker?.cpu_usage || 'N/A'}</p>
                </div>
              </div>
            </div>

            {/* Personality */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-white">🧬 Personality</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="form-label">Soul Status</label>
                  <p className={`text-lg font-bold ${worker?.personality?.soul_status === 'online' ? 'text-green-400' : 'text-red-400'}`}>
                    {worker?.personality?.soul_status || 'Unknown'}
                  </p>
                </div>
                <div>
                  <label className="form-label">Core DNA</label>
                  <p className="text-white text-sm">{worker?.personality?.core_dna || 'N/A'}</p>
                </div>
                <div>
                  <label className="form-label">Alignment Vector</label>
                  <p className="text-white text-sm">{worker?.personality?.alignment_vector || 'N/A'}</p>
                </div>
                <div>
                  <label className="form-label">Voice Profile</label>
                  <p className="text-white text-sm">{worker?.personality?.voice_profile || 'N/A'}</p>
                </div>
                <div>
                  <label className="form-label">Memory Seeds</label>
                  <p className="text-white">{worker?.personality?.memory_seeds || 0}</p>
                </div>
                <div>
                  <label className="form-label">Greeting Template</label>
                  <p className="text-white text-sm italic">"{worker?.personality?.greeting_template || 'N/A'}"</p>
                </div>
                <div>
                  <label className="form-label">Activation Timestamp</label>
                  <p className="text-white text-sm">{worker?.personality?.activation_timestamp || 'Never'}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Configuration and Logs Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            {/* Configuration */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-white">Configuration</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="form-label">Capabilities</label>
                  <div className="flex flex-wrap gap-2">
                    {worker?.capabilities?.map((cap, index) => (
                      <span key={index} className="px-2 py-1 bg-blue-600 text-white text-xs rounded">
                        {cap}
                      </span>
                    )) || <span className="text-gray-400">None</span>}
                  </div>
                </div>
                <div>
                  <label className="form-label">Environment</label>
                  <p className="text-white font-mono text-sm">{worker?.environment || 'N/A'}</p>
                </div>
                <div>
                  <label className="form-label">Version</label>
                  <p className="text-white">{worker?.version || 'N/A'}</p>
                </div>
              </div>
            </div>

            {/* Logs */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-white">Recent Activity</h2>
              </div>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {worker?.logs?.map((log, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-gray-700 rounded">
                    <span className="text-xs text-gray-400 whitespace-nowrap">{log.timestamp}</span>
                    <span className={`px-2 py-1 rounded text-xs ${
                      log.level === 'ERROR' ? 'bg-red-600' :
                      log.level === 'WARN' ? 'bg-yellow-600' :
                      'bg-blue-600'
                    }`}>
                      {log.level}
                    </span>
                    <span className="text-white text-sm flex-1">{log.message}</span>
                  </div>
                )) || <p className="text-gray-400">No recent activity</p>}
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 card">
            <div className="card-header">
              <h2 className="text-xl font-semibold text-white">Actions</h2>
            </div>
            <div className="flex flex-wrap gap-4">
              <button className="btn-primary">
                Restart Worker
              </button>
              <button className="btn-secondary">
                Update Configuration
              </button>
              <button className="btn-danger">
                Terminate Worker
              </button>
              <button className="btn-secondary">
                View Full Logs
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}