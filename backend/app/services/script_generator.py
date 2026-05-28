from typing import Dict, List

class ScriptGenerator:
    """Generate setup scripts for different platforms"""
    
    def generate_bash_script(
        self,
        repo_name: str,
        languages: List[str],
        frameworks: List[str],
        dependencies_file: str = None
    ) -> str:
        """
        Generate bash script for macOS/Linux
        
        Args:
            repo_name: Name of the repository
            languages: List of detected languages
            frameworks: List of detected frameworks
            dependencies_file: Content of package file (requirements.txt, package.json, etc.)
        
        Returns:
            Bash script as string
        """
        
        script_lines = [
            "#!/bin/bash",
            "set -e",
            "",
            "echo '🚀 DevOnboard Setup Script'",
            f"echo 'Setting up {repo_name}...'",
            "echo ''",
            ""
        ]
        
        # Detect Python
        if 'Python' in languages or any('django' in f.lower() or 'flask' in f.lower() for f in frameworks):
            script_lines.extend([
                "# Python Setup",
                "echo '📦 Setting up Python environment...'",
                "",
                "# Check Python installation",
                "if ! command -v python3 &> /dev/null; then",
                "    echo 'Python 3 not found. Installing...'",
                "    if [[ \"$OSTYPE\" == \"darwin\"* ]]; then",
                "        brew install python3",
                "    elif [[ \"$OSTYPE\" == \"linux-gnu\"* ]]; then",
                "        sudo apt-get update",
                "        sudo apt-get install -y python3 python3-pip python3-venv",
                "    fi",
                "fi",
                "",
                "# Create virtual environment",
                "python3 -m venv venv",
                "source venv/bin/activate",
                "",
                "# Install dependencies",
                "if [ -f \"requirements.txt\" ]; then",
                "    echo 'Installing Python dependencies...'",
                "    pip install -r requirements.txt",
                "fi",
                ""
            ])
        
        # Detect Node.js
        if 'JavaScript' in languages or 'TypeScript' in languages or any('react' in f.lower() or 'vue' in f.lower() or 'angular' in f.lower() for f in frameworks):
            script_lines.extend([
                "# Node.js Setup",
                "echo '📦 Setting up Node.js environment...'",
                "",
                "# Check Node.js installation",
                "if ! command -v node &> /dev/null; then",
                "    echo 'Node.js not found. Installing...'",
                "    if [[ \"$OSTYPE\" == \"darwin\"* ]]; then",
                "        brew install node",
                "    elif [[ \"$OSTYPE\" == \"linux-gnu\"* ]]; then",
                "        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -",
                "        sudo apt-get install -y nodejs",
                "    fi",
                "fi",
                "",
                "# Install dependencies",
                "if [ -f \"package.json\" ]; then",
                "    echo 'Installing Node.js dependencies...'",
                "    npm install",
                "fi",
                ""
            ])
        
        # Docker check
        script_lines.extend([
            "# Check Docker (optional)",
            "if command -v docker &> /dev/null; then",
            "    echo '🐳 Docker is installed'",
            "    if [ -f \"docker-compose.yml\" ]; then",
            "        echo 'Found docker-compose.yml'",
            "        echo 'Run: docker-compose up -d'",
            "    fi",
            "fi",
            ""
        ])
        
        # Final message
        script_lines.extend([
            "echo ''",
            "echo '✅ Setup complete!'",
            f"echo 'Your {repo_name} environment is ready.'",
            "echo ''",
            "echo 'Next steps:'",
            "echo '  1. Review the README for usage instructions'",
            "echo '  2. Run the application'",
            "echo '  3. Start developing!'",
            ""
        ])
        
        return "\n".join(script_lines)
    
    def generate_powershell_script(
        self,
        repo_name: str,
        languages: List[str],
        frameworks: List[str],
        dependencies_file: str = None
    ) -> str:
        """
        Generate PowerShell script for Windows
        
        Args:
            repo_name: Name of the repository
            languages: List of detected languages
            frameworks: List of detected frameworks
            dependencies_file: Content of package file
        
        Returns:
            PowerShell script as string
        """
        
        script_lines = [
            "# DevOnboard Setup Script for Windows",
            f"Write-Host '🚀 Setting up {repo_name}...' -ForegroundColor Green",
            "Write-Host ''",
            ""
        ]
        
        # Python setup
        if 'Python' in languages or any('django' in f.lower() or 'flask' in f.lower() for f in frameworks):
            script_lines.extend([
                "# Python Setup",
                "Write-Host '📦 Setting up Python environment...' -ForegroundColor Cyan",
                "",
                "# Check Python installation",
                "$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue",
                "if (-not $pythonInstalled) {",
                "    Write-Host 'Python not found. Please install Python 3.9+ from python.org' -ForegroundColor Red",
                "    exit 1",
                "}",
                "",
                "# Create virtual environment",
                "python -m venv venv",
                "",
                "# Activate virtual environment",
                ".\\venv\\Scripts\\Activate.ps1",
                "",
                "# Install dependencies",
                "if (Test-Path requirements.txt) {",
                "    Write-Host 'Installing Python dependencies...'",
                "    pip install -r requirements.txt",
                "}",
                ""
            ])
        
        # Node.js setup
        if 'JavaScript' in languages or 'TypeScript' in languages or any('react' in f.lower() or 'vue' in f.lower() for f in frameworks):
            script_lines.extend([
                "# Node.js Setup",
                "Write-Host '📦 Setting up Node.js environment...' -ForegroundColor Cyan",
                "",
                "# Check Node.js installation",
                "$nodeInstalled = Get-Command node -ErrorAction SilentlyContinue",
                "if (-not $nodeInstalled) {",
                "    Write-Host 'Node.js not found. Please install from nodejs.org' -ForegroundColor Red",
                "    exit 1",
                "}",
                "",
                "# Install dependencies",
                "if (Test-Path package.json) {",
                "    Write-Host 'Installing Node.js dependencies...'",
                "    npm install",
                "}",
                ""
            ])
        
        # Final message
        script_lines.extend([
            "Write-Host ''",
            "Write-Host '✅ Setup complete!' -ForegroundColor Green",
            f"Write-Host 'Your {repo_name} environment is ready.'",
            "Write-Host ''",
            "Write-Host 'Next steps:' -ForegroundColor Yellow",
            "Write-Host '  1. Review the README for usage instructions'",
            "Write-Host '  2. Run the application'",
            "Write-Host '  3. Start developing!'",
            ""
        ])
        
        return "\n".join(script_lines)
    
    def generate_docker_compose(
        self,
        repo_name: str,
        languages: List[str],
        frameworks: List[str],
        has_database: bool = False
    ) -> str:
        """
        Generate docker-compose.yml file
        
        Args:
            repo_name: Name of the repository
            languages: List of detected languages
            frameworks: List of detected frameworks
            has_database: Whether the project uses a database
        
        Returns:
            docker-compose.yml content as string
        """
        
        compose_lines = [
            "version: '3.8'",
            "",
            "services:"
        ]
        
        # Python/Django/Flask service
        if 'Python' in languages:
            compose_lines.extend([
                "  app:",
                "    build: .",
                "    ports:",
                "      - \"8000:8000\"",
                "    volumes:",
                "      - .:/app",
                "    environment:",
                "      - DEBUG=True",
            ])
            
            if has_database:
                compose_lines.extend([
                "      - DATABASE_URL=postgresql://postgres:postgres@db:5432/devonboard",
                "    depends_on:",
                "      - db"
                ])
            
            compose_lines.append("")
        
        # Node.js service
        if 'JavaScript' in languages or 'TypeScript' in languages:
            compose_lines.extend([
                "  frontend:",
                "    build:",
                "      context: .",
                "      dockerfile: Dockerfile",
                "    ports:",
                "      - \"3000:3000\"",
                "    volumes:",
                "      - .:/app",
                "      - /app/node_modules",
                "    environment:",
                "      - NODE_ENV=development",
                ""
            ])
        
        # Database service
        if has_database:
            compose_lines.extend([
                "  db:",
                "    image: postgres:14",
                "    environment:",
                "      - POSTGRES_DB=devonboard",
                "      - POSTGRES_USER=postgres",
                "      - POSTGRES_PASSWORD=postgres",
                "    ports:",
                "      - \"5432:5432\"",
                "    volumes:",
                "      - postgres_data:/var/lib/postgresql/data",
                ""
            ])
        
        # Volumes
        if has_database:
            compose_lines.extend([
                "volumes:",
                "  postgres_data:",
                ""
            ])
        
        return "\n".join(compose_lines)