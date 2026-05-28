import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'

export default function Results() {
  const [result, setResult] = useState(null)
  const [activeTab, setActiveTab] = useState('readme')
  const [copied, setCopied] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const savedResult = localStorage.getItem('devonboard_result')
    if (savedResult) {
      setResult(JSON.parse(savedResult))
    } else {
      navigate('/')
    }
  }, [navigate])

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text)
    setCopied(label)
    setTimeout(() => setCopied(''), 2000)
  }

  const downloadFile = (content, filename) => {
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  if (!result) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
    </div>
  )

  const tabs = [
    { id: 'readme', label: '📄 README', content: result.documentation?.readme },
    { id: 'setup', label: '📋 Setup Guide', content: result.documentation?.setup_guide },
    { id: 'architecture', label: '🏗️ Architecture', content: result.documentation?.architecture },
    { id: 'bash', label: '🐧 Bash Script', content: result.scripts?.bash },
    { id: 'powershell', label: '💻 PowerShell', content: result.scripts?.powershell },
    { id: 'docker', label: '🐳 Docker', content: result.scripts?.docker_compose },
  ]

  const downloadMap = {
    readme: { file: 'README.md' },
    setup: { file: 'SETUP.md' },
    architecture: { file: 'ARCHITECTURE.md' },
    bash: { file: 'setup.sh' },
    powershell: { file: 'setup.ps1' },
    docker: { file: 'docker-compose.yml' },
  }

  const activeContent = tabs.find(t => t.id === activeTab)?.content || ''

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">
            {result.repository?.name}
          </h1>
          <p className="text-slate-400 mt-1">
            {result.repository?.languages?.join(', ')} · 
            {result.repository?.frameworks?.join(', ')} · 
            {result.repository?.file_count} files
          </p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg transition-colors text-sm"
        >
          ← Generate Another
        </button>
      </div>

      {/* Success Banner */}
      <div className="bg-green-500/10 border border-green-500/20 rounded-xl px-4 py-3 mb-6 flex items-center gap-3">
        <span className="text-green-400 text-lg">✅</span>
        <span className="text-green-300">Complete onboarding package generated successfully!</span>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-6">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-blue-500 text-white'
                : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl overflow-hidden">
        
        {/* Content Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/50">
          <span className="text-slate-400 text-sm">
            {tabs.find(t => t.id === activeTab)?.label}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => copyToClipboard(activeContent, activeTab)}
              className="bg-slate-700 hover:bg-slate-600 text-slate-300 px-3 py-1.5 rounded-lg text-sm transition-colors"
            >
              {copied === activeTab ? '✅ Copied!' : '📋 Copy'}
            </button>
            <button
              onClick={() => downloadFile(activeContent, downloadMap[activeTab].file)}
              className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm transition-colors"
            >
              ⬇️ Download
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          {['bash', 'powershell', 'docker'].includes(activeTab) ? (
            // Code view for scripts
            <pre className="text-green-400 font-mono text-sm whitespace-pre-wrap leading-relaxed">
              {activeContent}
            </pre>
          ) : (
            // Markdown view for documentation
            <div className="prose prose-invert prose-slate max-w-none">
              <ReactMarkdown>{activeContent}</ReactMarkdown>
            </div>
          )}
        </div>
      </div>

      {/* Download All Button */}
      <div className="mt-6 flex justify-center">
        <button
          onClick={() => {
            tabs.forEach(tab => {
              if (tab.content) {
                downloadFile(tab.content, downloadMap[tab.id].file)
              }
            })
          }}
          className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold px-8 py-3 rounded-xl transition-all"
        >
          ⬇️ Download All Files
        </button>
      </div>

    </div>
  )
}