import { Link } from 'react-router-dom'
import { Cpu } from 'lucide-react'

export default function Navbar() {
  return (
    <nav className="border-b border-slate-800 bg-slate-900/95 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        <div className="flex justify-between items-center h-16">

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
  <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
    <Cpu size={16} className="text-white" />
  </div>
  <span className="text-white font-bold text-xl">
    DevOnboard
  </span>
</Link>

          {/* Navigation */}
          <div className="flex items-center gap-6">

            <Link
              to="/"
              className="text-slate-400 hover:text-white transition-colors"
            >
              Home
            </Link>

            <Link
              to="/dashboard"
              className="text-slate-400 hover:text-white transition-colors"
            >
              Dashboard
            </Link>

            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-white transition-colors"
            >
              API Docs
            </a>

          </div>

        </div>

      </div>
    </nav>
  )
}