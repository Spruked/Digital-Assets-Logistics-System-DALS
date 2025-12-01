import { useState, useEffect } from 'react'
import Layout from '../../components/Layout'

export default function WorkerRegistry() {
  const [workers, setWorkers] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, active, inactive

  useEffect(() => {
    fetchWorkers()
    // Set up real-time updates
    const interval = setInterval(fetchWorkers, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchWorkers = async () => {
    try {
      const response = await fetch('/api/workers/')
      if (response.ok) {
        const data = await response.json()
        setWorkers(data)
      }
    } catch (error) {
      console.error('Failed to fetch workers:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredWorkers = workers.filter(worker => {
    if (filter === 'all') return true
    return worker.status === filter
  })

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'inactive': return 'bg-gray-500'
      case 'forging': return 'bg-blue-500'
      case 'failed': return 'bg-red-500'
      default: return 'bg-yellow-500'
    }
  }

  const inspectWorker = (serial) => {
    window.open(`/workers/${serial}`, `Inspect ${serial}`, 'width=1300,height=900,scrollbars=yes,resizable=yes')
  }

  const deleteWorker = async (serial) => {
    if (!confirm(`Are you sure you want to delete worker ${serial}?`)) return

    try {
      const response = await fetch(`/api/workers/${serial}`, { method: 'DELETE' })
      if (response.ok) {
        fetchWorkers() // Refresh the list
      } else {
        alert('Failed to delete worker')
      }
    } catch (error) {
      console.error('Delete error:', error)
      alert('Error deleting worker')
    }
  }

  if (loading) {
    return (
      <Layout title="Worker Registry">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto mb-4"></div>
            <p className="text-gray-400">Loading worker registry...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Worker Registry">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">📋 Worker Registry</h1>
            <p className="text-gray-400">Real-time worker monitoring and management</p>
          </div>

          <div className="flex items-center space-x-4">
            {/* Filter */}
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            >
              <option value="all">All Workers</option>
              <option value="active">Active Only</option>
              <option value="inactive">Inactive Only</option>
              <option value="forging">Forging</option>
            </select>

            {/* Refresh */}
            <button
              onClick={fetchWorkers}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors"
            >
              🔄 Refresh
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-2xl font-bold text-blue-400">{workers.length}</div>
            <div className="text-gray-400 text-sm">Total Workers</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-2xl font-bold text-green-400">
              {workers.filter(w => w.status === 'active').length}
            </div>
            <div className="text-gray-400 text-sm">Active</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-2xl font-bold text-blue-400">
              {workers.filter(w => w.status === 'forging').length}
            </div>
            <div className="text-gray-400 text-sm">Forging</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-2xl font-bold text-red-400">
              {workers.filter(w => w.status === 'failed').length}
            </div>
            <div className="text-gray-400 text-sm">Failed</div>
          </div>
        </div>

        {/* Worker Table */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Serial
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Template
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {filteredWorkers.map((worker) => (
                  <tr key={worker.serial} className="hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(worker.status)} mr-3`}></div>
                        <span className="text-sm text-gray-300 capitalize">{worker.status}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-white">{worker.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-300 font-mono">{worker.serial}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs rounded-full bg-purple-900/50 text-purple-300">
                        {worker.template}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {new Date(worker.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => inspectWorker(worker.serial)}
                          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs transition-colors"
                        >
                          🔍 Inspect
                        </button>
                        <button
                          onClick={() => deleteWorker(worker.serial)}
                          className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-xs transition-colors"
                        >
                          🗑️ Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredWorkers.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📋</div>
              <h3 className="text-xl font-medium text-gray-400 mb-2">No workers found</h3>
              <p className="text-gray-500">
                {filter === 'all' ? 'Create your first worker to get started.' : `No ${filter} workers found.`}
              </p>
            </div>
          )}
        </div>

        {/* Real-time indicator */}
        <div className="mt-4 flex items-center text-sm text-gray-400">
          <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
          Real-time updates every 5 seconds
        </div>
      </div>
    </Layout>
  )
}