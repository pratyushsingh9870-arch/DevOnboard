import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { generateComplete } from '../services/api'

export default function Home() {
  const [repoUrl, setRepoUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [step, setStep] = useState('')
  const navigate = useNavigate()

  const handleGenerate = async (e) => {
    e.preventDefault()
    
    if (!repoUrl.trim()) {
      setError('Please enter a GitHub repository URL')
      return
    }

    if (!repoUrl.includes('github.com')) {
      setError('Please enter a valid GitHub URL (e.g., https://github.com/user/repo)')
      return
    }

    setLoading(true)
    setError('')

    try {
      setStep('🔍 Analyzing repository...')
      await new Promise(r => setTimeout(r, 1000))
      
      setStep('🤖 Generating documentation with AI...')
     const result = await generateComplete(repoUrl)
      
      if (result.success) {
        setStep('✅ Documentation ready!')
        // Store result in localStorage to pass to Results page
        localStorage.setItem('devonboard_result', JSON.stringify(result))
        localStorage.setItem('devonboard_repo_url', repoUrl)
        navigate('/results')
      } else {
        setError(result.error || 'Failed to generate documentation')
      }
    } catch (err) {
    console.error('Full error:', err)
    
    if (err.code === 'ECONNABORTED' || err.message.includes('timeout')) {
        setError('Generation is taking longer than expected. Please try again with a smaller repository.')
    } else if (err.response) {
        setError(`Server error: ${err.response.data?.detail || 'Unknown error'}`)
    } else {
        setError('Cannot connect to backend. Make sure it is running on port 8000!')
    }
      
    } finally {
      setLoading(false)
      setStep('')
    }
  }

  return (
    <div className="min-h-screen">
      
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 pt-20 pb-16 text-center">
        
        {/* Badge */}
        <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-4 py-2 mb-8">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
          <span className="text-blue-400 text-sm font-medium">AI-Powered Developer Onboarding</span>
        </div>

        {/* Headline */}
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          Onboard developers
          <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
            10x faster
          </span>
        </h1>

        {/* Subheadline */}
        <p className="text-xl text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed">
          Paste any GitHub URL and get a professional README, setup guides, 
          and platform-specific setup scripts in seconds.
        </p>

        {/* Input Form */}
        <form onSubmit={handleGenerate} className="max-w-2xl mx-auto mb-8">
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/username/repository"
              className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-5 py-4 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors text-lg"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 text-white font-semibold px-8 py-4 rounded-xl transition-colors text-lg whitespace-nowrap"
            >
              {loading ? 'Generating...' : 'Generate Docs →'}
            </button>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="mt-4 flex items-center justify-center gap-3 text-slate-400">
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span>{step}</span>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-4 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 text-red-400">
              {error}
            </div>
          )}
        </form>

        {/* Example repos */}
        <div className="flex flex-wrap justify-center gap-2 text-sm">
          <span className="text-slate-500">Try with:</span>
          {[
            'facebook/react',
            'django/django',
            'vuejs/vue'
          ].map(repo => (
            <button
              key={repo}
              onClick={() => setRepoUrl(`https://github.com/${repo}`)}
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              {repo}
            </button>
          ))}
        </div>

      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: '📄',
              title: 'AI Documentation',
              desc: 'Auto-generates professional README files with features, installation steps, and usage examples.'
            },
            {
              icon: '⚡',
              title: 'Setup Scripts',
              desc: 'Creates platform-specific scripts for macOS, Linux, and Windows. Docker support included.'
            },
            {
              icon: '🔍',
              title: 'Tech Detection',
              desc: 'Automatically detects programming languages, frameworks, and tools used in the project.'
            }
          ].map((feature, i) => (
            <div key={i} className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6 hover:border-blue-500/30 transition-colors">
              <div className="text-3xl mb-4">{feature.icon}</div>
              <h3 className="text-white font-semibold text-lg mb-2">{feature.title}</h3>
              <p className="text-slate-400 leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Stats Section */}
      <section className="max-w-7xl mx-auto px-4 pb-16">
        <div className="bg-slate-800/30 border border-slate-700/50 rounded-2xl p-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            {[
              { value: '85%', label: 'Faster Onboarding' },
              { value: '30s', label: 'Generation Time' },
              { value: '3+', label: 'Script Formats' },
              { value: '100%', label: 'Automated' },
            ].map((stat, i) => (
              <div key={i}>
                <div className="text-3xl font-bold text-blue-400 mb-1">{stat.value}</div>
                <div className="text-slate-400 text-sm">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

    </div>
  )
}