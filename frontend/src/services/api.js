import axios from 'axios'

// Use the environment variable when available.
// Otherwise, use the local FastAPI backend during development.
const BACKEND_URL =
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: BACKEND_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000,
})

export const generateComplete = async (repoUrl) => {
  const response = await api.post('/api/docs/generate-complete', {
    repo_url: repoUrl,
  })

  return response.data
}

export const getRepositories = async () => {
  const response = await api.get('/api/repos/list')
  return response.data
}

export default api