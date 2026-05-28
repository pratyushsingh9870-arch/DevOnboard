import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getRepositories } from '../services/api'

export default function Dashboard() {
  const [repos, setRepos] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchRepos = async () => {
      try {
        const data = await getRepositories()
        setRepos(data.repositories || [])
      } catch (err) {
        console.error('Failed to fetch repos:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchRepos()
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
    </div>
  )

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-white">Repository Dashboard</h1>
        <button
          onClick={() => navigate('/')}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors text-sm"
        >
          + Analyze New Repo
        </button>
      </div>

      {repos.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">📭</div>
          <h3 className="text-xl font-semibold text-white mb-2">No repositories yet</h3>
          <p className="text-slate-400 mb-6">Analyze your first repository to get started</p>
          <button
            onClick={() => navigate('/')}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-xl transition-colors"
          >
            Analyze Repository
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {repos.map((repo) => (
            <div
              key={repo.id}
              className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-5 hover:border-blue-500/30 transition-all cursor-pointer"
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-white font-semibold">{repo.name}</h3>
                <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full">
                  {repo.primary_language || 'Unknown'}
                </span>
              </div>
              <p className="text-slate-400 text-sm mb-4 line-clamp-2">
                {repo.description || 'No description'}
              </p>
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span>⭐ {repo.stars}</span>
                <span>📁 {repo.file_count} files</span>
                <span>🕒 {new Date(repo.last_analyzed).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  )
}