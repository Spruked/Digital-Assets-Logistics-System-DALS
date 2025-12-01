import { useState, useEffect } from 'react'
import Layout from '../../components/Layout'

export default function WorkerForge() {
  const [templates, setTemplates] = useState([])
  const [formData, setFormData] = useState({
    name: '',
    template: 'standard',
    dryRun: true,
    atomic: true,
    manifest: true
  })
  const [isForging, setIsForging] = useState(false)
  const [forgeProgress, setForgeProgress] = useState(0)
  const [forgeStatus, setForgeStatus] = useState('')
  const [validationResult, setValidationResult] = useState(null)

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
    }
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const validateConfig = async () => {
    try {
      const response = await fetch('/api/workers/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          template: formData.template
        })
      })

      const result = await response.json()
      setValidationResult(result)

      if (result.valid) {
        alert(`✅ Configuration valid!\n\nEstimated size: ${result.estimated_size}\nResources needed: ${result.resources_needed}`)
      } else {
        alert(`❌ Validation failed:\n${result.issues.join('\n')}`)
      }
    } catch (error) {
      console.error('Validation error:', error)
      alert('Error validating configuration')
    }
  }

  const forgeWorker = async () => {
    if (!formData.name.trim()) {
      alert('Please enter a worker name')
      return
    }

    setIsForging(true)
    setForgeProgress(0)
    setForgeStatus('Initializing forge...')

    try {
      const response = await fetch('/api/workers/forge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          template: formData.template,
          options: {
            dry_run: formData.dryRun,
            atomic: formData.atomic,
            manifest: formData.manifest
          }
        })
      })

      if (response.ok) {
        const result = await response.json()

        // Simulate progress updates
        const steps = [
          'Configuration validated',
          'Resources allocated',
          'Cryptographic keys injected',
          'Docker container built',
          'Manifest generated',
          'Worker finalized'
        ]

        for (let i = 0; i < steps.length; i++) {
          await new Promise(resolve => setTimeout(resolve, 800))
          setForgeProgress(((i + 1) / steps.length) * 100)
          setForgeStatus(steps[i])
        }

        if (formData.dryRun) {
          alert(`✅ Dry run completed!\n\nWorker would be created with serial: ${result.serial}`)
        } else {
          alert(`✅ Worker forged successfully!\n\nName: ${result.name}\nSerial: ${result.serial}\nStatus: ${result.status}`)
          // Reset form
          setFormData({
            name: '',
            template: 'standard',
            dryRun: true,
            atomic: true,
            manifest: true
          })
        }
      } else {
        const error = await response.json()
        alert(`❌ Forge failed: ${error.detail || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Forge error:', error)
      alert('Error forging worker')
    } finally {
      setIsForging(false)
      setForgeProgress(0)
      setForgeStatus('')
    }
  }

  const clearForm = () => {
    setFormData({
      name: '',
      template: 'standard',
      dryRun: true,
      atomic: true,
      manifest: true
    })
    setValidationResult(null)
  }

  return (
    <Layout title="Worker Forge">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">⚒️ Worker Forge v2.0</h1>
          <p className="text-gray-400">Create new workers using industrial-grade cloning technology</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Forge Form */}
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h2 className="text-xl font-semibold text-white mb-6">Forge Configuration</h2>

            <div className="space-y-6">
              {/* Worker Name */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Worker Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., Alice-Prime, Bob-Worker"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isForging}
                />
              </div>

              {/* Template Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Worker Template
                </label>
                <select
                  name="template"
                  value={formData.template}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isForging}
                >
                  {templates.map(template => (
                    <option key={template.id} value={template.id}>
                      {template.name} - {template.base_resources}
                    </option>
                  ))}
                </select>
              </div>

              {/* Forge Options */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-3">
                  Forge Options
                </label>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="dryRun"
                      checked={formData.dryRun}
                      onChange={handleInputChange}
                      className="mr-3"
                      disabled={isForging}
                    />
                    <span className="text-sm text-gray-300">Dry Run (Validate Only)</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="atomic"
                      checked={formData.atomic}
                      onChange={handleInputChange}
                      className="mr-3"
                      disabled={isForging}
                    />
                    <span className="text-sm text-gray-300">Atomic Operations</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="manifest"
                      checked={formData.manifest}
                      onChange={handleInputChange}
                      className="mr-3"
                      disabled={isForging}
                    />
                    <span className="text-sm text-gray-300">Generate Manifest</span>
                  </label>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3">
                <button
                  onClick={validateConfig}
                  disabled={isForging}
                  className="flex-1 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 rounded-md text-white font-medium transition-colors"
                >
                  ✅ Validate
                </button>
                <button
                  onClick={forgeWorker}
                  disabled={isForging}
                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-md text-white font-medium transition-colors"
                >
                  {isForging ? 'Forging...' : '⚒️ Forge Worker'}
                </button>
                <button
                  onClick={clearForm}
                  disabled={isForging}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-600 rounded-md text-white font-medium transition-colors"
                >
                  🗑️ Clear
                </button>
              </div>
            </div>
          </div>

          {/* Forge Progress & Status */}
          <div className="space-y-6">
            {/* Progress Display */}
            {isForging && (
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Forge Progress</h3>

                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-300 mb-2">
                    <span>{forgeStatus}</span>
                    <span>{Math.round(forgeProgress)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${forgeProgress}%` }}
                    ></div>
                  </div>
                </div>

                <div className="text-sm text-gray-400">
                  Industrial-grade worker cloning in progress...
                </div>
              </div>
            )}

            {/* Validation Results */}
            {validationResult && (
              <div className={`rounded-lg border p-4 ${
                validationResult.valid
                  ? 'bg-green-900/20 border-green-500/30'
                  : 'bg-red-900/20 border-red-500/30'
              }`}>
                <h3 className={`text-lg font-semibold mb-2 ${
                  validationResult.valid ? 'text-green-400' : 'text-red-400'
                }`}>
                  {validationResult.valid ? '✅ Validation Passed' : '❌ Validation Failed'}
                </h3>

                {validationResult.valid ? (
                  <div className="text-sm text-gray-300">
                    <p><strong>Estimated Size:</strong> {validationResult.estimated_size}</p>
                    <p><strong>Resources Needed:</strong> {validationResult.resources_needed}</p>
                  </div>
                ) : (
                  <div className="text-sm text-red-300">
                    <strong>Issues:</strong>
                    <ul className="list-disc list-inside mt-1">
                      {validationResult.issues.map((issue, index) => (
                        <li key={index}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Template Info */}
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Selected Template</h3>

              {(() => {
                const selectedTemplate = templates.find(t => t.id === formData.template)
                return selectedTemplate ? (
                  <div className="text-sm text-gray-300">
                    <p className="font-medium text-white mb-2">{selectedTemplate.name}</p>
                    <p className="mb-2">{selectedTemplate.description}</p>
                    <p><strong>Base Resources:</strong> {selectedTemplate.base_resources}</p>
                    <p><strong>Version:</strong> {selectedTemplate.version}</p>
                  </div>
                ) : (
                  <p className="text-gray-400">Loading template information...</p>
                )
              })()}
            </div>

            {/* Forge Features */}
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-400 mb-4">🔧 Forge Features v2.0</h3>
              <ul className="text-sm text-gray-300 space-y-2">
                <li>✅ <strong>Staging:</strong> Atomic operations prevent partial failures</li>
                <li>✅ <strong>Manifest Hashing:</strong> Cryptographic integrity verification</li>
                <li>✅ <strong>Dry Run:</strong> Validate before committing resources</li>
                <li>✅ <strong>Idempotent:</strong> Safe to retry failed operations</li>
                <li>✅ <strong>Multi-Monitor:</strong> Pop-out windows for control centers</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}