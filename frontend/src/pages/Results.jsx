import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { 
  FileText, BookOpen, Layout, 
  Terminal, Monitor, Box, 
  Copy, Download, ArrowLeft, Check
} from 'lucide-react'

const TABS = [
  { id: 'readme',         label: 'README',      file: 'README.md',           icon: FileText },
  { id: 'setup_guide',    label: 'Setup Guide', file: 'SETUP.md',            icon: BookOpen },
  { id: 'architecture',   label: 'Architecture',file: 'ARCHITECTURE.md',     icon: Layout },
  { id: 'bash',           label: 'Bash Script', file: 'setup.sh',            icon: Terminal },
  { id: 'powershell',     label: 'PowerShell',  file: 'setup.ps1',           icon: Monitor },
  { id: 'docker_compose', label: 'Docker',      file: 'docker-compose.yml',  icon: Box },
]

export default function Results() {
  const [result, setResult] = useState(null)
  const [activeTab, setActiveTab] = useState('readme')
  const [copied, setCopied] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const saved = localStorage.getItem('devonboard_result')
    if (!saved) navigate('/')
    else setResult(JSON.parse(saved))
  }, [navigate])

  const getContent = (tabId) => {
    if (!result) return ''
    const docKeys = ['readme', 'setup_guide', 'architecture']
    if (docKeys.includes(tabId)) return result.documentation?.[tabId] || ''
    return result.scripts?.[tabId] || ''
  }

  const copyContent = () => {
    navigator.clipboard.writeText(getContent(activeTab))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
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

  const downloadAll = () => {
    TABS.forEach(tab => {
      const content = getContent(tab.id)
      if (content) downloadFile(content, tab.file)
    })
  }

  const isCode = ['bash', 'powershell', 'docker_compose'].includes(activeTab)
  const activeTabData = TABS.find(t => t.id === activeTab)

  if (!result) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">

      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">
            {result.repository?.name}
          </h1>
          <div className="flex flex-wrap gap-3 mt-2">
            {result.repository?.languages?.map(lang => (
              <span key={lang} className="text-xs bg-slate-700 text-slate-300 px-2 py-1 rounded">
                {lang}
              </span>
            ))}
            {result.repository?.frameworks?.map(fw => (
              <span key={fw} className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded">
                {fw}
              </span>
            ))}
            <span className="text-xs text-slate-500">
              {result.repository?.file_count} files
            </span>
          </div>
        </div>
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-white text-sm px-4 py-2 rounded-lg transition-colors"
        >
          <ArrowLeft size={14} />
          New Repo
        </button>
      </div>

      {/* Success Banner */}
      <div className="bg-green-500/10 border border-green-500/20 rounded-xl px-4 py-3 mb-6 text-green-300 text-sm flex items-center gap-2">
        <Check size={16} />
        Complete onboarding package generated — 6 files ready to download
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-4">
        {TABS.map(tab => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'
              }`}
            >
              <Icon size={14} />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Content Box */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl overflow-hidden">

        {/* Toolbar */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-slate-700/50">
          <span className="text-slate-400 text-sm font-mono">
            {activeTabData?.file}
          </span>
          <div className="flex gap-2">
            <button
              onClick={copyContent}
              className="flex items-center gap-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm px-3 py-1.5 rounded-lg transition-colors"
            >
              {copied ? <Check size={13} /> : <Copy size={13} />}
              {copied ? 'Copied' : 'Copy'}
            </button>
            <button
              onClick={() => downloadFile(getContent(activeTab), activeTabData?.file)}
              className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm px-3 py-1.5 rounded-lg transition-colors"
            >
              <Download size={13} />
              Download
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[55vh] overflow-y-auto">
          {isCode ? (
            <pre className="text-green-400 font-mono text-sm whitespace-pre-wrap leading-relaxed">
              {getContent(activeTab)}
            </pre>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none
              prose-headings:text-white
              prose-p:text-slate-300
              prose-strong:text-white
              prose-code:text-blue-300
              prose-pre:bg-slate-900
              prose-a:text-blue-400
              prose-li:text-slate-300
            ">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {getContent(activeTab)}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>

      {/* Download All */}
      <div className="mt-6 flex justify-center">
        <button
          onClick={downloadAll}
          className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white font-semibold px-10 py-3 rounded-xl transition-all shadow-lg shadow-blue-500/20"
        >
          <Download size={16} />
          Download All Files
        </button>
      </div>

    </div>
  )
}