import { useState, useEffect } from 'react'
import Layout from '../../components/Layout'

export default function WorkerTemplates() {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/workers/templates/')
      if (response.ok) {
        const data = await response.json()
        setTemplates(data)
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Layout title="Worker Templates">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
            <p className="text-gray-400">Loading worker templates...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Worker Templates">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">📄 Worker Templates</h1>
          <p className="text-gray-400">Manage and customize worker blueprints for different use cases</p>
        </div>

        {/* Templates Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <div key={template.id} className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-purple-500 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="text-3xl mb-2">📄</div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  template.type === 'general' ? 'bg-blue-900/50 text-blue-300' :
                  template.type === 'advanced' ? 'bg-purple-900/50 text-purple-300' :
                  'bg-green-900/50 text-green-300'
                }`}>
                  {template.type}
                </span>
              </div>

              <h3 className="text-xl font-semibold text-white mb-2">{template.name}</h3>
              <p className="text-gray-400 text-sm mb-4">{template.description}</p>

              <div className="space-y-2 text-sm text-gray-300 mb-6">
                <div><strong>Base Resources:</strong> {template.base_resources}</div>
                <div><strong>Version:</strong> {template.version}</div>
              </div>

              <div className="flex space-x-2">
                <button className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm font-medium transition-colors">
                  📋 Use Template
                </button>
                <button className="px-3 py-2 bg-gray-600 hover:bg-gray-700 rounded text-sm font-medium transition-colors">
                  ✏️ Edit
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Create New Template */}
        <div className="mt-8 bg-gray-800 rounded-lg border border-gray-700 p-6">
          <div className="text-center">
            <div className="text-4xl mb-4">➕</div>
            <h3 className="text-xl font-semibold text-white mb-2">Create New Template</h3>
            <p className="text-gray-400 mb-6">Design custom worker blueprints for specialized use cases</p>
            <button className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg text-white font-medium transition-colors">
              Create Template
            </button>
          </div>
        </div>

        {/* Template Features */}
        <div className="mt-8 bg-purple-900/20 border border-purple-500/30 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-purple-400 mb-4">🎨 Template System Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-white mb-2">Standard Template</h4>
              <p className="text-sm text-gray-300">Basic worker with standard resource allocation. Perfect for general-purpose tasks.</p>
            </div>
            <div>
              <h4 className="font-medium text-white mb-2">Specialized Template</h4>
              <p className="text-sm text-gray-300">Enhanced worker with advanced capabilities and security features.</p>
            </div>
            <div>
              <h4 className="font-medium text-white mb-2">Custom Template</h4>
              <p className="text-sm text-gray-300">Fully customizable worker template for unique requirements.</p>
            </div>
            <div>
              <h4 className="font-medium text-white mb-2">Future: AI Templates</h4>
              <p className="text-sm text-gray-300">Templates optimized for AI workloads with GPU acceleration support.</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}