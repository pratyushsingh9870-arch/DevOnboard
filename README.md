<div align="center">
██████╗ ███████╗██╗   ██╗ ██████╗ ███╗   ██╗██████╗  ██████╗  █████╗ ██████╗ ██████╗
██╔══██╗██╔════╝██║   ██║██╔═══██╗████╗  ██║██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
██║  ██║█████╗  ██║   ██║██║   ██║██╔██╗ ██║██████╔╝██║   ██║███████║██████╔╝██║  ██║
██║  ██║██╔══╝  ╚██╗ ██╔╝██║   ██║██║╚██╗██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║
██████╔╝███████╗ ╚████╔╝ ╚██████╔╝██║ ╚████║██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
╚═════╝ ╚══════╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝

### Stop writing docs manually. Let AI do it in 30 seconds.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

[ Live Demo](https://devonboard.vercel.app) · [📖 API Docs](https://devonboard-api.onrender.com/docs) · [ Report Bug](https://github.com/pratyushsingh9870-arch/DevOnboard/issues)

</div>

---

## The Problem
New developer joins your team.
Week 1: Figuring out what the project does.
Week 2: Setting up their environment.
Week 3: Making their first commit.
2-4 weeks wasted. Every. Single. Time.

**DevOnboard fixes this in 30 seconds.**

---

## How It Works
BEFORE DevOnboard              AFTER DevOnboard
─────────────────              ────────────────
 Read scattered docs          Paste GitHub URL
 Manually set up env          Wait 30 seconds
 Ask seniors questions         Get everything:
 2-4 weeks to first commit       ├── Professional README
├── Setup scripts (Mac/Win/Docker)
├── Architecture overview
└── Installation guide
                             First commit in 2 days

---

## Features

| | Feature | What It Does |
|---|---------|-------------|
|  | **Smart Analysis** | Reads actual file contents — not just file names |
|  | **AI Documentation** | GPT-powered README with real context from your code |
|  | **Script Generator** | Bash + PowerShell + Docker scripts auto-tailored to your stack |
|  | **Architecture Docs** | Understands and explains your project structure |
|  | **Tech Detection** | Identifies languages, frameworks, and databases automatically |
|  | **History** | Every generated doc saved — retrieve anytime via API |

---

## Demo

```bash
# Input
curl -X POST https://devonboard-api.onrender.com/api/docs/generate-complete \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/your/repo"}'
```

```json
// Output (30 seconds later)
{
  "success": true,
  "documentation": {
    "readme":       "# YourProject\n\n...(500+ word professional README)...",
    "setup_guide":  "## Prerequisites\n\n...(step-by-step guide)...",
    "architecture": "## Architecture\n\n...(system overview)..."
  },
  "scripts": {
    "bash":         "#!/bin/bash\n...(Mac/Linux setup script)...",
    "powershell":   "# Windows Setup\n...(PowerShell script)...",
    "docker_compose": "version: '3.8'\n...(Docker config)..."
  }
}
```

---

## Tech Stack
┌─────────────────────────────────────────────────┐
│                   DevOnboard                     │
│                                                  │
│  Frontend          Backend           External    │
│  ─────────         ───────           ────────    │
│  React 18          FastAPI           GitHub API  │
│  Tailwind CSS      SQLAlchemy        OpenRouter  │
│  Axios             PostgreSQL        GPT Model   │
│  React Router      Pydantic                      │
└─────────────────────────────────────────────────┘

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- GitHub Personal Access Token
- OpenRouter API Key (free tier available)

### Installation

```bash
# 1. Clone
git clone https://github.com/pratyushsingh9870-arch/DevOnboard.git
cd DevOnboard

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Start backend
python -m uvicorn app.main:app --reload
# Running at http://127.0.0.1:8000

# 5. Frontend setup (new terminal)
cd ../frontend
npm install
npm run dev
# Running at http://localhost:5173
```

### Environment Variables

```env
GITHUB_TOKEN=ghp_your_github_token
OPENROUTER_API_KEY=sk-or-your_openrouter_key
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///./devonboard.db
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/docs/generate-complete` | Generate full onboarding package |
| `POST` | `/api/docs/generate-scripts` | Generate setup scripts only |
| `GET` | `/api/docs/repo/{name}` | Retrieve saved documentation |
| `POST` | `/api/repos/analyze` | Analyze repository structure |
| `GET` | `/api/repos/list` | List all analyzed repositories |
| `GET` | `/api/docs/test` | Test AI connection |
| `GET` | `/api/repos/test` | Test GitHub connection |
| `GET` | `/health` | API health check |

Full interactive docs: **[/docs](https://devonboard-api.onrender.com/docs)**

---

## Project Structure
DevOnboard/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── docs.py          # Documentation endpoints
│   │   │   └── repos.py         # Repository endpoints
│   │   ├── models/
│   │   │   ├── repository.py    # DB model
│   │   │   └── documentation.py # DB model
│   │   ├── services/
│   │   │   ├── ai_service.py        # OpenRouter integration
│   │   │   ├── github_service.py    # GitHub API integration
│   │   │   └── script_generator.py  # Bash/PS/Docker scripts
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings
│   │   └── database.py          # SQLAlchemy setup
│   ├── requirements.txt
│   └── .env.example
└── frontend/
├── src/
│   ├── pages/
│   │   ├── Home.jsx          # Landing + URL input
│   │   ├── Results.jsx       # Generated docs viewer
│   │   └── Dashboard.jsx     # Repository history
│   ├── components/
│   │   └── Navbar.jsx
│   └── services/
│       └── api.js            # Axios configuration
└── package.json

---

## Business Case
Average developer onboarding: 2-4 weeks
With DevOnboard:               2 days
Time saved per hire:    ~10 days of engineering time
Cost saved per hire:    ~$4,800 (at $60/hr avg)
Generation time:        < 60 seconds
Cost per generation:    ~$0.015

---

## Roadmap

- [x] GitHub API integration
- [x] AI documentation generation
- [x] Multi-platform setup scripts
- [x] React frontend with dark theme
- [x] Database persistence
- [ ] User authentication
- [ ] Team collaboration features
- [ ] VS Code extension
- [ ] AI code navigator (RAG-based Q&A)
- [ ] Analytics dashboard

---

## Contributing

```bash
# Fork → Clone → Branch → Code → PR

git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
# Open Pull Request
```

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting PRs.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built by [Pratyush Singh](https://github.com/pratyushsingh9870-arch)**

*If DevOnboard saved you time, consider giving it a ⭐*

</div>